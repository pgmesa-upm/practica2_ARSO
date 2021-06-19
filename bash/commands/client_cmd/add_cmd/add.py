
import logging

# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from ...reused_definitions import reused_opts, reused_flags
# Imports para la funcion asociada al comando
from program.platform.machines import client
from program.platform import platform
from program import program
from program.platform import platform
from ...start_cmd.start import start
from ...reused_functions import get_cl_opts

def get_add_cmd():
    msg = """creates a container with lynx installed 
    in order to act as a client"""
    add = Command("add", description=msg)
    # ++++++++++++++++++++++++++++
    name = _def_name_opt()
    add.add_option(name)
    # ++++++++++++++++++++++++++++
    image = _def_image_opt()
    add.add_option(image)
    # Flags ----------------------
    add.add_flag(reused_flags["-l"])
    add.add_flag(reused_flags["-t"])
    
    return add

def _def_image_opt():
    image = Option(
        "--image", description="allows to specify the image",
        extra_arg=True, mandatory=True
    )
    return image

def _def_name_opt():
    name = Option(
        "--name", description="allows to specify the name",
        extra_arg=True, mandatory=True
    )
    return name
    
# --------------------------------------------------------------------
# --------------------------------------------------------------------
add_logger = logging.getLogger(__name__)
def add(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={}):
    if not platform.is_deployed():
        msg = " La plataforma no ha sido desplegada"
        add_logger.error(msg)
        return
    cl = client.get_client()
    if cl is not None: 
        msg = (" Ya existe un contenedor cliente en la plataforma, " + 
                "no se permiten mas")
        add_logger.error(msg)
        return
    image, name = get_cl_opts(options, flags)
    if "--name" in options:
        name = options["--name"][0]
    cl = client.create_client(name=name, image=image)
    if cl is not None:
        program.list_lxc_containers(cl) 
        msg = (f" Cliente '{cl}' inicializado\n")
        add_logger.info(msg)
        add_logger.info(" Estableciendo conexiones ...")
        platform.update_conexions()
        add_logger.info(" Conexiones establecidas\n")
        if "-l" in flags:
            start(args=[cl.name], options=options, flags=flags)
    else:
        msg = (f" Fallo al crear el contenedor cliente")
        add_logger.error(msg)