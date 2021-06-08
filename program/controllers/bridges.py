
import logging

from dependencies.register import register
from dependencies.utils.tools import objectlist_as_dict
from dependencies.lxc.lxc_classes.bridge import Bridge, LxcNetworkError

if True:
    from dependencies.utils.decorators import catch_foreach
else:
    from dependencies.utils.decorators import (
        catch_foreach_thread as catch_foreach
    )

# --------------- CONTROLADOR DE BRIDGES (PUENTES) -------------------
# --------------------------------------------------------------------
# Proporciona funciones para manipular los bridges de forma sencilla
# y maneja las excepciones y errores que se puedan dar a la hora
# de manipularlos (catch_foreach, se encarga de atrapar las 
# excepciones cada vez que se llama a la funcion)
# --------------------------------------------------------------------

# Id con el que se van a guardar los bridges en el registro
ID = "bridges"
bgs_logger = logging.getLogger(__name__)
# -------------------------------------------------------------------
@catch_foreach(bgs_logger)
def init(b:Bridge=None):
    bgs_logger.info(f" Creando bridge '{b.name}'...")
    try:
        b.create()
    except LxcNetworkError as err:
        err_msg = str(err)
        if "already exists" in err_msg:
            warn_msg = (f" El bridge '{b.name}' ya existe, " + 
                         "no hace falta crearlo")
            bgs_logger.warning(warn_msg)
            _add_bridge(b)
            raise LxcNetworkError()
        else:
            raise LxcNetworkError(err_msg)
    else:
        bgs_logger.info(f" bridge '{b.name}' creado con exito")
    _add_bridge(b)

# -------------------------------------------------------------------
@catch_foreach(bgs_logger)
def delete(b:Bridge=None):
    bgs_logger.info(f" Eliminando bridge '{b.name}'...")
    try:
        b.delete()
    except LxcNetworkError as err:
        err_msg = str(err)
        if "The network is currently in use" in err_msg:
            warn_msg = (f" El bridge '{b.name}' esta siendo usado " + 
                         "fuera del programa, se eliminara de la " +
                         "plataforma pero seguira existiendo")
            bgs_logger.warning(warn_msg)
            _update_bridges(b, remove=True)
            raise LxcNetworkError()
        else:
            raise LxcNetworkError(err_msg)
    else:
        bgs_logger.info(f" bridge '{b.name}' eliminado con exito")
    _update_bridges(b, remove=True)

# -------------------------------------------------------------------
def attach(cs_name:str, to_bridge:Bridge, with_eth:str):
    """Añade un contenedor al bridge

    Args:
        cs_name (str): Nombre del contenedor a añadir
        to_bridge (Bridge): Bridge al que se va a añadir el contenedor
    """
    bridge = to_bridge
    msg = (f" Agregando '{cs_name}' al bridge '{bridge.name}' " + 
           f"usando la tarjeta de red '{with_eth}'...")
    bgs_logger.info(msg)
    try:
        bridge.add_container(cs_name, with_eth)
        bgs_logger.info(f" '{cs_name}' agregado con exito")
    except LxcNetworkError as err:
        bgs_logger.error(err)
    _update_bridges(bridge)
    
# -------------------------------------------------------------------   
def _update_bridges(*bs_to_update:Bridge, remove=False):
    """Actualiza el objeto de un bridge en el registro

    Args:
        b_to_update (Bridge): Contenedor a actualizar
        remove (bool, optional): Si es verdadero, se elimina el
            contenedor del registro. Por defecto es False
    """
    bgs = register.load(ID)
    bgs_dict = objectlist_as_dict(bgs, key_attribute="name")
    for b in bs_to_update:
        if b.name in bgs_dict:
            if remove:
                bgs_dict.pop(b.name)
            else:
                bgs_dict[b.name] = b
    if len(bgs_dict) == 0:
        register.remove(ID)
    else:
        register.update(ID, list(bgs_dict.values()))

def _add_bridge(b_to_add:Bridge):
    """Añade un bridge al registro

    Args:
        b_to_add (Bridge): Bridge a añadir
    """
    bgs = register.load(register_id=ID)
    if bgs == None:
        register.add(ID, [b_to_add])
    else:
        register.update(ID, b_to_add, override=False)
        
# -------------------------------------------------------------------      

