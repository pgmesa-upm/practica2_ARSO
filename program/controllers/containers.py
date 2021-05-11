
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
def connect_to_networks(c:Container):
    """Conecta un contenedor a sus networks previamente añadidas

    Args:
        c (Container): Contenedor a manipular
        with_ip (str): ip con la que se quiere conectar a la subred
        to_network (str): subred a la que se quiere conectar
    """
    for eth, ip in c.networks.items():
        if c.connected_networks[eth]: continue
        cs_logger.info(f" Conectando {c.tag} '{c.name}' usando la " + 
                                f"ip '{ip}' a la network '{eth}'...")
        try:
            c.connect_to_network(eth)
            cs_logger.info(f" Conexion realizada con exito")
        except Exception as err:
            cs_logger.error(err)
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
