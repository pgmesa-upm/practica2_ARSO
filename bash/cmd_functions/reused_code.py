
import logging
from logging import Logger
from contextlib import suppress

import dependencies.lxc.lxc as lxc
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
global_image = None; checked = False
def _check_global_image(options:dict, flags:list):
    global global_image, checked
    if not checked:
        image = None
        if "--image" in options:
            image = _check_image(options["--image"]["args"][0], flags)
        global_image = image
        checked = True
    return global_image
    
def get_servers_opts(options:dict, flags:list):
    simage = _check_global_image(options, flags); names = []
    if "--simage" in options:
        simage = _check_image(options["--simage"]["args"][0], flags)
    if "--name" in options:   
        names = options["--name"]["args"]
    return simage, names

def get_lb_opts(options:dict, flags:list):
    lbimage = _check_global_image(options, flags); algorithm = None
    if "--lbimage" in options:
        lbimage = _check_image(options["--lbimage"]["args"][0], flags)
    if "--balance" in options:
        algorithm = options["--balance"]["args"][0]
    return lbimage, algorithm

def get_cl_opts(options:dict, flags:list):
    climage = _check_global_image(options, flags); clname = "cl"
    if "--climage" in options:
        climage = _check_image(options["--climage"]["args"][0], flags)
    with suppress(KeyError):
        clname = options["--client"]["args"][0]
    return climage, clname

def get_db_opts(options:dict,flags:list):
    dbimage = _check_global_image(options, flags)
    if "--dbimage" in options:
        dbimage = _check_image(options["--dbimage"]["args"][0], flags)
    return dbimage

def _check_image(image:str, flags:list):
    if "-y" not in flags:
        im_list = lxc.lxc_image_list()
        fingerprints = im_list.keys()
        aliases = []
        for f in fingerprints:
            aliases.append(im_list[f]["ALIAS"])
        if image not in fingerprints and image not in aliases:
            print(f"La imagen '{image}' no se encuentra en el " +
                "repositorio local de aplicaciones")
            answer = input("¿Utilizar de todos modos?(y/n): ")
            if answer.lower() != "y":
                return None
    return image