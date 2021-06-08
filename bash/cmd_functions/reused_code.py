
import logging
from logging import Logger
from os import name
from contextlib import suppress

from program.controllers import containers
from dependencies.register import register
from dependencies.utils.tools import objectlist_as_dict, remove_many


def target_containers(logger:Logger=None):
    """Decorador que permite reutilizar el codigo de algunos comandos.
    Comprueba que haya contenedores creados y despues devuelve los 
    contenedores diana sobre los que se va a aplicar el comando.
    Nota: 
    Si no se pasa ningun contenedor en el comando (argumentos que 
    recibe get_targets) se asume que se quiere aplicar el comando a
    todos los contenedores existentes.

    Args:
        logger (Logger, optional): logger del fichero que va a 
            utilizar el decorador

    Returns:
        function: devuelve la funcion que ha llamado al decorador
            con el decorador ya aplicado
    """
    if logging == None:
        logger = logging.getLogger(__name__)
    def _target_containers(cmd):
        def get_targets(*args, **opt_args):
            cs = register.load(containers.ID)
            if cs == None:
                msg = " No existen contenedores creados por el programa"
                logger.error(msg)
                return
            # Comprobamos si hay que operar sobre todos los existentes 
            # o solo algunos en concreto
            names_given = list(args)
            c_dict = objectlist_as_dict(cs, "name")
            target_cs = cs
            if len(args) != 0: 
                valid_names = filter(lambda name: name in c_dict, names_given)
                target_cs = list(map(lambda valid: c_dict[valid], valid_names))
            # Notificamos los incorrectos. Eliminamos los nombres validos 
            # de los que nos han pasado y si siguen quedando nombres 
            # significa que no son validos. 
            remove_many(names_given, *c_dict.keys())
            for wrong in names_given:
                err_msg = f" No existe el contenedor '{wrong}' en este programa"
                logger.error(err_msg)
            # En caso de que haya algun contenedor valido
            if len(target_cs) != 0:
                cmd(*target_cs, **opt_args)
        return get_targets
    return _target_containers

# --------------------------------------------------------------------

def get_servers_opts(options:dict):
    simage = None; names = []
    if "--image" in options:
        simage = options["--image"]["args"][0]
    if "--simage" in options:
        simage = options["--simage"]["args"][0] 
    if "--name" in options:   
        names = options["--name"]["args"]
    return simage, names

def get_lb_opts(options:dict):
    lbimage = None; algorithm = None
    if "--image" in options:
        lbimage = options["--image"]["args"][0]
    if "--lbimage" in options:
        lbimage = options["--lbimage"]["args"][0]
    if "--balance" in options:
        algorithm = options["--balance"]["args"][0]
    return lbimage, algorithm

def get_cl_opts(options:dict):
    climage = None; clname = "cl"
    if "--image" in options:
        climage = options["--image"]["args"][0]
    if "--climage" in options:
        climage = options["--climage"]["args"][0]
    with suppress(IndexError):
        clname = options["--client"]["args"][0]
    return climage, clname

def get_db_opts(options:dict):
    dbimage = None
    if "--image" in options:
        dbimage = options["--image"]["args"][0]
    if "--dbimage" in options:
        dbimage = options["--dbimage"]["args"][0]
    return dbimage