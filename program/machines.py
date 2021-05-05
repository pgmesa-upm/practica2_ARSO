
import program.controllers.bridges as bridges
import program.controllers.containers as containers
import dependencies.register.register as register
from dependencies.lxc_classes.container import Container
from dependencies.lxc_classes.bridge import Bridge
from dependencies.utils.tools import objectlist_as_dict

# --------------------- MAQUINAS DEL PROGRAMA ------------------------
# --------------------------------------------------------------------
# Este fichero se encarga de proporcionar funciones para crear los
# objetos de los contenedores y bridges que se van a utilizar en este
# programa
# --------------------------------------------------------------------

# Tags permitidos para los contenedores de este programa
SERVER = "server"; LB = "load balancer"; CLIENT  = "client"
# Imagen por defecto con la que se van a crear los contenedores
default_image = "ubuntu:18.04"
# --------------------------------------------------------------------
def get_loadbalancer(image:str=default_image) -> Container:
    """Devuelve el objeto del LB configurado

    Args:
        image (str, optional): imagen del contenedor a usar.
            Por defecto se utiliza la especificada en default_image.

    Returns:
        Container: objeto del balanceador de carga configurado
    """
    return Container("lb", image, tag=LB)

def get_clients(image:str()=default_image) -> Container:
    """Devuelve el objeto del cliente configurado

    Args:
        image (str, optional): imagen del contenedor a usar.
            Por defecto se utiliza la especificada en default_image.

    Returns:
        Container: objeto del cliente configurado
    """
    return Container("cl", image, tag=CLIENT)

def get_servers(num:int(), *names, image:str()=default_image) -> list:
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
    servs = []
    server_names = _process_names(num, *names)
    for name in server_names:
        servs.append(Container(name, image, tag=SERVER))
    return servs

def get_bridges(numBridges:int) -> list:
    """Devuelve los objetos de los bridges que se vayan a crear 
    configurados

    Args:
        numBridges (int): Numero de bridges a crear

    Returns:
        list: lista de objetos de tipo Bridge
    """
    bgs = []
    for i in range(numBridges):
        b_name = f"lxdbr{i}"
        b = Bridge(
            b_name, 
            ethernet=f"eth{i}",
            ipv4_nat=True, ipv4_addr=f"10.0.{i}.1/24"
        )
        bgs.append(b)
    return bgs

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