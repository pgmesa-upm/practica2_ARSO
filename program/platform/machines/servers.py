
import logging
import subprocess

from program.controllers import containers
import dependencies.register.register as register
from dependencies.lxc_classes.container import Container
from dependencies.utils.tools import objectlist_as_dict
from dependencies.utils.lxc_functions import (
    checkin_lxclist,
    lxclist_as_dict
)
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
    # el balanceador o ya se ha creado antes y esta disponible
    if image == None:
        img_saved = register.load(IMG_ID)
        if img_saved is None:
            image = _config_image()
        else:
            # Comprobamos que la imagen no se haya borrado en lxc
            fgp = img_saved["fingerprint"]
            msg = f" Imagen anterior guardada de servidores '{fgp}'"
            serv_logger.debug(msg)
            if checkin_lxclist(["lxc", "image", "list"], 1, fgp):
                # Vemos el alias de la imagen por si se ha modificado 
                process = subprocess.run(
                    ["lxc","image","list"],
                    stdout=subprocess.PIPE
                )
                lista = process.stdout.decode()
                images = lxclist_as_dict(lista)
                headers = list(images.keys())
                alias = ""
                for i, fg in enumerate(images[headers[1]]):
                    if fg == fgp:
                        alias = images[headers[0]][i]
                        break
                image_info = {"alias": alias, "fingerprint": fgp}
                register.update(IMG_ID, image_info, override=True)
                image = alias
                if alias == "": image = fgp
                msg = (" Alias actual de la imagen" + 
                       f" de servidores -> '{alias}'")
                serv_logger.debug(msg)
            else:
                # Como se ha eliminado creamos otra nueva
                msg = (f" Imagen de servidores se ha borrado" + 
                        "desde fuera del programa")
                serv_logger.debug(msg)
                register.remove(IMG_ID)
                image = _config_image()
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
    msg = (f" Contenedor usado para crear imagen" + 
          f" del servidores -> '{name}'")
    serv_logger.debug(msg)
    serv = Container(name, default_image)
    # Lanzamos el contenedor e instalamos haproxy
    serv_logger.info(f" Lanzando '{name}'...")
    serv.init(); serv.start()
    serv_logger.info(" Instalando tomcat8 (puede tardar)...")
    serv.wait_for_startup()
    process = subprocess.run(
        ["lxc","exec",name,"--","apt","update"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    process = subprocess.run(
        ["lxc","exec",name,"--","apt","install","-y","tomcat8"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    if process.returncode == 0:
        serv_logger.info(" Tomcat8 instalado con exito")
    else:
        serv_logger.error(" Fallo al instalar tomcat8")
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
    serv.stop()
    process = subprocess.run(
        ["lxc", "publish", name, "--alias", alias],
        stdout=subprocess.PIPE
    )
    serv_logger.info(" Imagen base de servidores creada\n")
    # Eliminamos el contenedor
    serv.delete()
    # Guardamos la imagen en el registro y la devolvemos 
    # (obtenemos tambien la huella que le ha asignado lxc)
    process = subprocess.run(
        ["lxc","image","list"],
        stdout=subprocess.PIPE
    )
    images = lxclist_as_dict(process.stdout.decode())
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