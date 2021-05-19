
import os
import logging
from contextlib import suppress

from program.controllers import containers
from dependencies.register import register
from dependencies.lxc.lxc_classes.container import Container
from dependencies.utils.tools import objectlist_as_dict
from dependencies.lxc import lxc
from program.platform import platform
# --------------------------- SERVIDORES -----------------------------
# --------------------------------------------------------------------
# Este fichero se encarga de proporcionar funciones para crear y 
# configurar los objetos de los servidores que se van a utilizar en 
# la plataforma
# --------------------------------------------------------------------

serv_logger = logging.getLogger(__name__)
# Tag e id de registro para la imagen configurada
TAG = "server"; IMG_ID = "s_image"
# Puerto en que se van a ejecutar
PORT = 8080
# --------------------------------------------------------------------
def get_servers(num:int, *names, image:str=None) -> list:
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
    # Comprobamos que si hace falta configurar una imagen base para
    # los servidores o ya nos han pasado una o se ha creado antes 
    # y esta disponible 
    if image is None:
        if platform.is_imageconfig_needed(IMG_ID):
            image = _config_image()
        else:
            image_saved = register.load(IMG_ID)
            alias = image_saved["alias"]
            image = alias
            if alias == "": image = image_saved["fingerprint"]
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
        servers.append(server)
    return servers

def _config_image() -> str:
    serv_logger.info(" Creando la imagen base de los servidores...")
    # Vemos que no haya un contenedor con ese nombre ya
    name = "servconfig"
    j = 1
    while name in lxc.lxc_list():
        name = f"servconfig{j}"
        j += 1
    msg = (f" Contenedor usado para crear imagen " + 
          f"de servidores -> '{name}'")
    serv_logger.debug(msg)
    serv = Container(name, platform.default_image)
    # Lanzamos el contenedor e instalamos modulos
    serv_logger.info(f" Lanzando '{name}'...")
    serv.init(); serv.start()
    serv_logger.info(" Instalando tomcat8 (puede tardar)...")
    try:
        serv.update_apt()
        serv.install("tomcat8")
        serv_logger.info(" Tomcat8 instalado con exito")
    except lxc.LxcError as err:
        err_msg = (" Fallo al instalar tomcat8, " + 
                            "error de lxc: " + str(err))
        serv_logger.error(err_msg)
        return platform.default_image
    # Añadimos la aplicacion a los servidores 
    path = "/var/lib/tomcat8/webapps/"
    serv.execute(["rm", "-rf", path+"ROOT"])
    serv.push("program/resources/ROOT", path)
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
    serv.stop(); serv.publish(alias=alias)
    serv_logger.info(" Imagen base de servidores creada\n")
    # Eliminamos el contenedor
    serv.delete()
    # Guardamos la imagen en el registro y la devolvemos 
    # (obtenemos tambien la huella que le ha asignado lxc)
    images = lxc.lxc_image_list()
    fingerprint = ""
    for f, info in images.items():
        if info["ALIAS"] == alias:
            fingerprint = f
    image_info = {"alias": alias, "fingerprint": fingerprint}
    register.add(IMG_ID, image_info)
    return alias

# --------------------------------------------------------------------
def mark_htmlindexes(undo=False):
    # Para modificar el index.html de la aplicacion de cada servidor
    # y ver quien es quien. Replace elimina el index.html que haya
    # en el contenedor
    cs = register.load(containers.ID)
    if cs is None:
        serv_logger.error(" No hay contenedores creados")
        return
    servs = list(filter(lambda c: c.tag == TAG,cs))
    if len(servs) == 0:
        serv_logger.error(" No hay servidores en funcionamiento")
        return
    word1 = "Marcando"
    if undo:
        word1 = "Desmarcando"
    serv_logger.info(f" {word1} servidores...")
    index_dir = "/var/lib/tomcat8/webapps/ROOT/"
    index_path = index_dir+"index.html"
    for s in servs:
        if s.state != "RUNNING":
            serv_logger.error(f" El servidor {s.name} no esta arrancado")
            continue
        try:
            if s.marked and not undo: 
                serv_logger.error(f" El servidor {s.name} ya esta marcado")
                continue
            if not s.marked and undo:
                serv_logger.error(f" El servidor {s.name} no esta marcado")
                continue
        except:
            if undo: 
                serv_logger.error(f" El servidor {s.name} no esta marcado")
                continue
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
        old = "<html>"
        new = f"<html><h1> Servidor {s.name} </h1>"
        if undo:
            old = new
            new = "<html>"
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
            setattr(s, "marked", True)
        word2 = word1.lower().replace("n", "")
        serv_logger.info(f" Servidor '{s.name}' {word2}")
        os.remove("index.html")
    register.update(containers.ID, cs)

def change_app(app_path):
    cs = register.load(containers.ID)
    if cs is None:
        serv_logger.error(" No hay contenedores creados")
        return
    servs = list(filter(lambda c: c.tag == TAG,cs))
    if len(servs) == 0:
        serv_logger.error(" No hay servidores en funcionamiento")
        return
    webapps_dir = "/var/lib/tomcat8/webapps/"
    root_dir = "/var/lib/tomcat8/webapps/ROOT"
    for s in servs:
        if s.state != "RUNNING":
            serv_logger.error(f" El servidor {s.name} no esta arrancado")
            continue
        serv_logger.info(f" Actualizando aplicacion de servidor '{s.name}'")
        try: 
            # Eliminamos la aplicacion anterior
            s.execute(["rm", "-rf", root_dir])
        except lxc.LxcError as err:
            err_msg = (f" Error al eliminar la aplicacion anterior: {err}")
            serv_logger.error(err_msg)
            return
        try:
            s.push(app_path, webapps_dir)
        except lxc.LxcError as err:
            err_msg = (f" Error al añadir la aplicacion: {err}")
            serv_logger.error(err_msg)
            return
        msg = (f" Actualizacion de aplicacion de servidor '{s.name}' " + 
                    "realizada con exito")
        with suppress(Exception):
            s.marked = False
        register.update(containers.ID, cs)
        serv_logger.info(msg)
        
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

