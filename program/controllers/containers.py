
import logging
import subprocess
from time import sleep
from os import remove
from contextlib import suppress

import dependencies.register.register as register
from dependencies.utils.decorators import catch_foreach
from dependencies.lxc_classes.container import Container, LxcError

# ------------------ CONTROLADOR DE CONTENEDORES ---------------------
# --------------------------------------------------------------------
# Proporciona funciones para manipular los contenedores de forma
# sencilla y maneja las excepciones y errores que se puedan dar a la 
# hora de manipularlos (catch_foreach, se encarga de atrapar las 
# excepciones cada vez que se llama a la funcion)
# --------------------------------------------------------------------

# Id con el que se van a guardar los contenedores en el registro
ID = "containers"
cs_logger = logging.getLogger(__name__)
# --------------------------------------------------------------------
@catch_foreach(cs_logger)
def init(c:Container=None):            
    cs_logger.info(f" Inicializando {c.tag} '{c.name}'...")
    c.init()
    cs_logger.info(f" {c.tag} '{c.name}' inicializado con exito")
    _add_container(c)
    
# --------------------------------------------------------------------
@catch_foreach(cs_logger)
def start(c:Container):
    cs_logger.info(f" Arrancando {c.tag} '{c.name}'...")
    c.start()
    cs_logger.info(f" {c.tag} '{c.name}' arrancado con exito")
    _update_container(c)
        
# --------------------------------------------------------------------
@catch_foreach(cs_logger)
def pause(c:Container):
    cs_logger.info(f" Pausando {c.tag} '{c.name}'...")
    c.pause()
    cs_logger.info(f" {c.tag} '{c.name}' pausado con exito")
    _update_container(c)
        
# --------------------------------------------------------------------
@catch_foreach(cs_logger)
def stop(c:Container):
    cs_logger.info(f" Deteniendo {c.tag} '{c.name}'...")
    c.stop()
    cs_logger.info(f" {c.tag} '{c.name}' detenido con exito")
    _update_container(c)

# --------------------------------------------------------------------
@catch_foreach(cs_logger)
def delete(c:Container):
    with suppress(Exception):
        c.stop()
    cs_logger.info(f" Eliminando {c.tag} '{c.name}'...")
    c.delete()
    cs_logger.info(f" {c.tag} '{c.name}' eliminado con exito")
    _update_container(c, remove=True)

# --------------------------------------------------------------------
@catch_foreach(cs_logger)
def open_terminal(c:Container):
    c.open_terminal()
        
# --------------------------------------------------------------------
def connect(c:Container, with_ip:str, to_network:str):
    """Añade un contenedor a una network con la ip especificada

    Args:
        c (Container): Contenedor a manipular
        with_ip (str): ip con la que se quiere conectar a la subred
        to_network (str): subred a la que se quiere conectar
    """
    ip, eth = with_ip, to_network
    cs_logger.info(f" Conectando {c.tag} '{c.name}' usando la " + 
                            f"ip '{ip}' a la network '{eth}'...")
    try:
        c.add_to_network(eth, ip)
        cs_logger.info(f" Conexion realizada con exito")
    except LxcError as err:
        cs_logger.error(err)
    _update_container(c)

def configure_netfile(c:Container):
    """Genera el fichero de configuracion .yaml del contenedor y lo
    introduce en la carpeta correspondiente. Se arranca el contenedor
    y se espera a que se cree el sistema de ficheros entero para poder
    añadir el fichero a la ruta etc/netplan del contenedor

    Args:
        c (Container): Contenedor a configurar
    """
    networks = c.networks
    if len(networks) == 1 and list(networks.keys())[0] == "eth0": return
    config_file =("network:\n" +
                  "    version: 2\n" + 
                  "    ethernets:\n")
    for eth in networks:
        new_eth_config = (f"        {eth}:\n" + 
                            "            dhcp4: true\n")
        config_file += new_eth_config
    msg = (f" Configurando el net_file del {c.tag} '{c.name}'... " +
           "(Esta operacion puede tardar un rato dependiendo del PC " + 
           "o incluso saltar el timeout si es muy lento)")
    cs_logger.info(msg)
    cs_logger.debug("\n" + config_file)
    file_location = "50-cloud-init.yaml"
    with open(file_location, "w") as file:
        file.write(config_file)
    # El problema esta en que lo crea, pero al hacer start o debido a
    # que no se ha inicializado todavia, se crea el primer fichero 
    # sobrescribiendo al nuestro
    subprocess.run(["lxc","start",c.name])
    error = "Error: not found"
    time = 0
    t0 = 2
    timeout = 60
    path = f"{c.name}/etc/netplan/50-cloud-init.yaml"
    while "Error: not found" in error:
        if not time >= timeout:
            process = subprocess.run(
                ["lxc","file","delete", path],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE
            )
            error = process.stderr.decode().strip()
            msg = (f"Intentando acceder al fichero de configuracion " + 
                  f"de '{c.name}' (stderr = '{error}') -> " +
                  ("SUCCESS" if error == "" else "ERROR"))
            cs_logger.debug(msg)
            sleep(t0)
            time += t0
        else:
            subprocess.call(["lxc","stop",c.name])
            cs_logger.error(f" Error al añadir fichero de " + 
                            f"configuracion a '{c.name}' (timeout)")
            remove(file_location)
            return        
    subprocess.call(["lxc","file","push", file_location, path])
    subprocess.call(["lxc","stop",c.name])
    cs_logger.info(f" Net del {c.tag} '{c.name}' configurada con exito")
    remove(file_location)
    _update_container(c)
    
# --------------------------------------------------------------------    
def _update_container(c_to_update:Container, remove:bool=False):
    """Actualiza el objeto de un contenedor en el registro

    Args:
        c_to_update (Container): Contenedor a actualizar
        remove (bool, optional): Si es verdadero, se elimina el
            contenedor del registro. Por defecto es False
    """
    cs = register.load(ID)
    index = None
    for i, c in enumerate(cs):
        if c.name == c_to_update.name:
            index = i
            break
    if index != None:
        cs.pop(index)
        if remove:
            if len(cs) == 0:
                register.remove(ID)
                return
        else:
            cs.append(c_to_update)
        register.update(ID, cs)

def _add_container(c_to_add:Container):
    """Añade un contenedor al registro

    Args:
        c_to_add (Container): Contenedor a añadir
    """
    cs = register.load(register_id=ID)
    if cs == None:
        register.add(ID, [c_to_add])
    else:
        register.update(ID, c_to_add, override=False)
    
# --------------------------------------------------------------------
