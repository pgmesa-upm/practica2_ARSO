
import os
import logging

from program.controllers import containers
from dependencies.register import register
from dependencies.lxc.lxc_classes.container import Container
from dependencies.lxc import lxc
from program.platform import platform
from dependencies.utils.tools import concat_array

# --------------------------- SERVIDORES -----------------------------
# --------------------------------------------------------------------
# Este fichero se encarga de proporcionar funciones para crear y 
# configurar los objetos de los servidores que se van a utilizar en 
# la plataforma
# --------------------------------------------------------------------

serv_logger = logging.getLogger(__name__)
# Tag e id de registro para la imagen configurada
TAG = "server"; IMG_ID = "s_image"
# Puerto en que se van a ejecutar (default de tomcat8)
PORT = 8080
# Donde se guardan las aplicaciones (default de tomcat8)
tomcat_app_path = "/var/lib/tomcat8/webapps"
# --------------------------------------------------------------------
def create_servers(num:int, *names, image:str=None) -> list:
    """Devuelve los objetos de los servidores que se vayan a crear 
    configurados

    Args:
        num (int): numero de servidores a crear
        image (str, optional): imagen del contenedor a usar.
            Por defecto se utiliza la especificada en default_image.
        names: nombres proporcionados para los servidores

    Returns:
        list: lista de objetos de tipo Contenedor (servidores)
    """
    # Creamos los objetos de los servidores
    servers = []
    server_names = _process_names(num, *names)
    serv_logger.debug(f" Creando servidores con imagen {image}")
    cs = register.load(containers.ID)
    ips = []
    if cs is not None:
        for c in cs:
            ips.append(c.networks.get("eth0",""))
    for name in server_names:
        if image == None:
            server = Container(name, platform.default_image, tag=TAG)
        else:
            server = Container(name, image, tag=TAG)
        # Lo añadimos a una red con una ip que no este usando ningun
        # otro contenedor
        ip = "10.0.0.11"
        j = 1
        while ip in ips:
            j += 1
            ip = f"10.0.0.1{j}"
        ips.append(ip)
        server.add_to_network("eth0", with_ip=ip)
        setattr(server, "port", PORT)
        setattr(server, "app", None)
        setattr(server, "marked", False)
        servers.append(server)
    successful = _config_servs(*servers, image=image)
    return successful

# --------------------------------------------------------------------
def _config_servs(*servs, image=None) -> list:
    # Comprobamos que si hace falta configurar una imagen base para
    # los servidores en base a si ya la hemos creado antes o 
    #  nos han pasado una en concreto para usar
    servs = list(servs); successful = []
    serv_logger.info(f" Inicializando servidores '{concat_array(servs)}'")
    if image == None and platform.is_imageconfig_needed(IMG_ID):
        serv:Container = servs.pop(0)
        serv_logger.info(" Creando la imagen base de los servidores...")
        msg = (f" Contenedor usado para crear imagen " + 
            f"de servidores -> '{serv}'")
        serv_logger.debug(msg)
        # Lanzamos el contenedor e instalamos tomcat8
        containers.init(serv); containers.start(serv)
        serv_logger.info(f" Configurando {serv.tag} '{serv}'...")
        # Rearrancamos por si acaso para evitar fallos al instalar
        serv.restart() # Para evitar posibles fallos en la instalacion (dpkg)
        serv_logger.info(" Instalando tomcat8 (puede tardar)...")
        try:
            serv.update_apt()
            serv.install("tomcat8")
            serv_logger.info(" Tomcat8 instalado con exito")
        except lxc.LxcError as err:
            err_msg = (" Fallo al instalar tomcat8, " + 
                                "error de lxc: " + str(err))
            serv_logger.error(err_msg)
            image = platform.default_image
            setattr(serv, "has_config_error", True)
            for s in servs:
                setattr(s, "has_config_error", True)
            containers.stop(serv)
        else:
            _publish_tomcat_image(serv)
            msg = (" Configuracion de imagen base de servidores " + 
                   "realizada con exito\n")
            serv_logger.info(msg)
        successful.append(serv)
    if image == None:
        image_saved = register.load(IMG_ID)
        alias = image_saved["alias"]
        image = alias
        if alias == "": image = image_saved["fingerprint"]
        for s in servs: s.base_image = alias
    successful += containers.init(*servs)
    return successful

def _publish_tomcat_image(serv:Container):
    # Vemos que no existe una imagen con el alias que vamos a usar
    alias = "tomcat8_serv"
    k = 1
    images = lxc.lxc_image_list()
    aliases = list(map(lambda f: images[f]["ALIAS"], images))  
    while alias in aliases:
        alias = f"tomcat8_serv{k}"
        k += 1
    # Una vez el alias es valido publicamos la imagen
    msg = (f" Publicando imagen base de servidores " + 
        f"con alias '{alias}'...")
    serv_logger.info(msg)
    containers.stop(serv); serv.publish(alias=alias)
    serv_logger.info(" Publicacion completada")
    # Guardamos la imagen en el registro
    # (obtenemos tambien la huella que le ha asignado lxc)
    images = lxc.lxc_image_list()
    fingerprint = ""
    for f, info in images.items():
        if info["ALIAS"] == alias:
            fingerprint = f
    image_info = {"alias": alias, "fingerprint": fingerprint}
    register.add(IMG_ID, image_info)

# --------------------------------------------------------------------
def change_app(server:Container, app_path:str, name:str):
    webapps_dir = f"{tomcat_app_path}/"
    root_dir = f"{tomcat_app_path}/ROOT"
    if server.state != "RUNNING":
        err = f" El servidor {server.name} no esta arrancado"
        serv_logger.error(err)
        return
    # if server.app == name:
    #     err = (f" El servidor '{server.name}' ya esta usando la " + 
    #             f"aplicacion '{name}'")
    #     serv_logger.error(err)
    #     return
    msg = f" Actualizando aplicacion de servidor '{server.name}'..."
    serv_logger.info(msg)
    try: 
        # Eliminamos la aplicacion anterior
        server.execute(["rm", "-rf", root_dir])
    except lxc.LxcError as err:
        err_msg = (f" Error al eliminar la aplicacion anterior: {err}")
        serv_logger.error(err_msg)
        return
    try:
        server.push(app_path, webapps_dir)
    except lxc.LxcError as err:
        err_msg = (f" Error al añadir la aplicacion: {err}")
        serv_logger.error(err_msg)
        return
    msg = (f" Actualizacion de aplicacion de servidor '{server.name}' " + 
                "realizada con exito")
    server.app = name
    server.marked = False
    containers.update_containers(server)
    serv_logger.info(msg)

# --------------------------------------------------------------------
def mark_htmlindexes(s:Container, undo=False):
    # Para modificar el index.html de la aplicacion de cada servidor
    # y ver quien es quien. Replace elimina el index.html que haya
    # en el contenedor
    word1 = "Marcando"
    if undo:
        word1 = "Desmarcando"
    index_dir = f"{tomcat_app_path}/ROOT/"
    index_path = index_dir+"index.html"
    if s.state != "RUNNING":
        serv_logger.error(f" El servidor {s.name} no esta arrancado")
        return
    if s.marked and not undo: 
        serv_logger.error(f" El servidor {s.name} ya esta marcado")
        return
    if not s.marked and undo:
        serv_logger.error(f" El servidor {s.name} no esta marcado")
        return
    serv_logger.info(f" {word1} servidor '{s.name}'")
    pulled_file = "index.html"
    try:  
        s.pull(index_path, pulled_file)
    except lxc.LxcError as err:
        err_msg = (f" Error al descargar el index.html " + 
                            f"del contenedor '{s.name}':" + str(err))
        serv_logger.error(err_msg)
        return
    with open(pulled_file, "r") as file:
        index = file.read()
    # Vemos donde hay que introducir/quitar la marca
    mark = f"\n<h1> Servidor {s.name} </h1>" 
    if not undo:
        simbol = "<html"
        chars = list(index)
        start = index.find(simbol)
        html_label = ""
        for i in range(start,len(chars)):
            char = chars[i]
            html_label += char
            if char == ">":
                break
        old = html_label
        new = html_label + mark
    else:
        old = mark
        new = ""
    # Marcamos o desmarcamos el index.html
    configured_index = index.replace(old, new)
    with open(pulled_file, "w") as f:
        f.write(configured_index)
    try:  
        s.push(pulled_file, index_dir)
    except lxc.LxcError as err:
        err_msg = (f" Error al enviar el index.html marcado" + 
                            f"al contenedor '{s.name}':" + str(err))
        serv_logger.error(err_msg)
        return
    if undo:
        s.marked = False
    else:
        s.marked = True
    word2 = word1.lower().replace("n", "")
    serv_logger.info(f" Servidor '{s.name}' {word2}")
    os.remove("index.html")
    containers.update_containers(s)
    
# --------------------------------------------------------------------
def _process_names(num:int, *names) -> list:
    """Se encarga de proporcionar una lista con nombres validos 
    para los contenedores que se vayan a crear. Mira en el registro
    los nombres existentes y crea otros nuevos no utilizados de la
    forma s_. Si se le han proporcionado nombres (names) los utiliza,
    es decir, solo crea los nombres que hagan falta que no se hayan
    proporcionado ya. Si se requieren 2 nombres y solo se le pasa 1 en
    names, se encarga de crear el que falta y que sea valido.

    Args:
        num (int): numero de nombres a crear

    Returns:
        list: lista con nombres para los servidores
    """
    j = 1
    cs = register.load(containers.ID)
    if cs == None:
        cs_names = []
    else:
        cs_names = list(map(lambda c: c.name, cs)) 
    existing_names = cs_names + list(lxc.lxc_list().keys())
    server_names = []
    for i in range(num):
        try:
            name = names[i] 
        except:
            # Si no nos han proporcionado mas nombres, buscamos
            # uno que no exista ya o no nos hayan pasado antes
            name = f"s{j}"
            j += 1
            while name in existing_names:   
                name = f"s{j}"
                j += 1
        existing_names.append(name)
        server_names.append(name)
    return server_names
# --------------------------------------------------------------------

