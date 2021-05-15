
import logging

from program.controllers import containers
from dependencies.register import register
from dependencies.lxc.lxc_classes.container import Container
from dependencies.utils.tools import objectlist_as_dict
from dependencies.lxc.lxc_functions import (
    checkin_lxclist,
    lxc_image_list,
    process_lxclist
)
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
# Imagen por defecto sobre la que se va a realizar la configuracion
default_image = "ubuntu:18.04"
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

def _config_image():
    serv_logger.info(" Creando la imagen base de los servidores...")
    # Vemos que no haya un contenedor con ese nombre ya
    name = "servconfig"
    j = 1
    while checkin_lxclist(["lxc", "list"], 0, name):
        name = f"servconfig{j}"
        j += 1
    msg = (f" Contenedor usado para crear imagen " + 
          f"de servidores -> '{name}'")
    serv_logger.debug(msg)
    serv = Container(name, default_image)
    # Lanzamos el contenedor e instalamos modulos
    serv_logger.info(f" Lanzando '{name}'...")
    serv.init(); serv.start()
    serv_logger.info(" Instalando tomcat8 (puede tardar)...")
    serv.update_apt()
    try:
        serv.install("tomcat8")
        serv_logger.info(" Tomcat8 instalado con exito")
    except:
        serv_logger.error(" Fallo al instalar tomcat8")
        return default_image
    # Vemos que no existe una imagen con el alias que vamos a usar
    alias = "tomcat8_serv"
    k = 1
    while checkin_lxclist(["lxc", "image", "list"], 0, alias):
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
    l = lxc_image_list()
    images = process_lxclist(l)
    headers = list(images.keys())
    fingerprint = ""
    for i, al in enumerate(images[headers[0]]):
        if al == alias:
            fingerprint = images[headers[1]][i]
    image_info = {"alias": alias, "fingerprint": fingerprint}
    register.add(IMG_ID, image_info)
    return alias

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
    server_names = []
    j = 1
    machine_names = objectlist_as_dict(
        register.load(containers.ID), 
        key_attribute="name"
    )
    if machine_names == None:
        machine_names = []
    for i in range(num):
        try:
            name = names[i] 
        except:
            # Si no nos han proporcionado mas nombres, buscamos
            # uno que no exista ya o no nos hayan pasado antes
            name = f"s{j}"
            j += 1
            while (name in server_names or 
                     name in machine_names):   
                name = f"s{j}"
                j += 1
        server_names.append(name)
    return server_names
# --------------------------------------------------------------------