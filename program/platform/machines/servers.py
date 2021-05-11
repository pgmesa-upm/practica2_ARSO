
import logging

from program.controllers import containers
import dependencies.register.register as register
from dependencies.lxc_classes.container import Container
from dependencies.utils.tools import objectlist_as_dict

# --------------------------- SERVIDORES -----------------------------
# --------------------------------------------------------------------
# Este fichero se encarga de proporcionar funciones para crear y 
# configurar los objetos de los servidores que se van a utilizar en 
# la plataforma
# --------------------------------------------------------------------

serv_logger = logging.getLogger(__name__)
# Tag e id de registro para la imagen configurada
TAG = "server"; IMG_ID = "s_image"
# Imagen por defecto sobre la que se va a realizar la configuracion
default_image = "ubuntu:18.04"
# --------------------------------------------------------------------
def get_servers(num:int, *names, image:str=default_image) -> list:
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
    pass

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