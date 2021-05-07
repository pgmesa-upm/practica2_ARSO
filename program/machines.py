
import subprocess
import logging

import program.functions as program
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

machine_logger = logging.getLogger(__name__)
# Tags permitidos para los contenedores de este programa
SERVER = "server"; LB = "load balancer"; CLIENT  = "client"
# Ids del registro donde se encuentra el nombre de las imagenes usadas
S_IMG = "s_image"; LB_IMG = "lb_image"; CL_IMG = "cl_image"
# Imagen por defecto con la que se van a crear los contenedores
default_image = "ubuntu:18.04"
# --------------------------------------------------------------------
def _checkin_lxclist(list_cmd:list, colum:int, val:str):
    process = subprocess.run(
        list_cmd,
        stdout=subprocess.PIPE
    )
    table = program.lxclist_as_dict(process.stdout.decode())
    headers = list(table.keys())
    if val in table[headers[colum]]:
        return True
    return False

# --------------------------------------------------------------------
def get_loadbalancer(image:str=None) -> Container:
    """Devuelve el objeto del LB configurado

    Args:
        image (str, optional): imagen del contenedor a usar.
            Si es None, crea una imagen propia para el balanceador
            configurada y funcional (permite actuar al contenedor 
            como un balanceador de trafico)

    Returns:
        Container: objeto del balanceador de carga configurado
    """
    if image == None:
        img_saved = register.load(LB_IMG)
        if img_saved is None:
            image = _configure_lbimage()
        else:
            # Comprobamos que la imagen no se haya borrado en lxc
            if _checkin_lxclist(["lxc", "image", "list"], 0, img_saved):
                image = img_saved
            else:
                register.remove(LB_IMG)
                image = _configure_lbimage()
    machine_logger.debug(f" Creando balanceador con imagen {image}")
    return Container("lb", image, tag=LB)

def _configure_lbimage() -> str:
    """Crea una imagen para el balanceador de carga completamente
    configurada y funcional a partir de la default_image

    Returns:
        str: alias de la imagen creada
    """
    machine_logger.info(" Creando la imagen base del balanceador...")
    # Vemos que no haya un contenedor con ese nombre ya
    name = "lbconfig"
    j = 1
    while _checkin_lxclist(["lxc", "list"], 0, name):
        name = f"lbconfig{j}"
        j += 1
    msg = f" Contenedor usado para crear la imagen del lb -> '{name}'"
    machine_logger.debug(msg)
    lb_c = Container(name, default_image)
    # Lanzamos el contenedor e instalamos haproxy
    lb_c.init(); lb_c.start()
    machine_logger.info(" Instalando haproxy (puede tardar)...")
    lb_c.wait_for_startup()
    process = subprocess.run(
        ["lxc","exec",name,"--","apt","update"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    process = subprocess.run(
        ["lxc","exec",name,"--","apt","install","-y","haproxy"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    if process.returncode == 0:
        machine_logger.info(" Haproxy instalado con exito")
    else:
        machine_logger.error(" Fallo al instalar haproxy")
    # Vemos que no existe una imagen con el alias que vamos a usar
    alias = "lb_haproxy"
    k = 1
    while _checkin_lxclist(["lxc", "image", "list"], 0, alias):
        alias = f"lb_haproxy_{k}"
        k += 1
    # Una vez el alias es valido publicamos la imagen
    msg = f" Publicando la imagen del lb con alias '{alias}'..."
    machine_logger.info(msg)
    lb_c.stop()
    process = subprocess.run(
        ["lxc", "publish", name, "--alias", alias],
        stdout=subprocess.PIPE
    )
    if process.returncode == 0:
        machine_logger.info(" Imagen base del balanceador creada\n")
    else:
        machine_logger.error(" Fallo al publicar la imagen del lb\n")
    # Eliminamos el contenedor
    lb_c.delete()
    # Guardamos la imagen en el registro y la devolvemos
    register.add(LB_IMG, alias)
    return alias
    
# --------------------------------------------------------------------
def get_clients(image:str()=default_image) -> Container:
    """Devuelve el objeto del cliente configurado

    Args:
        image (str, optional): imagen del contenedor a usar.
            Por defecto se utiliza la especificada en default_image.

    Returns:
        Container: objeto del cliente configurado
    """
    machine_logger.debug(f" Creando cliente con imagen {image}")
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
    machine_logger.debug(f" Creando servidores con imagen {image}")
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