
import logging

# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from ...reused_definitions import reused_opts, reused_flags
# Imports para la funcion asociada al comando
from program.platform.machines import data_base
from program.platform import platform
from program import program
from program.platform import platform
from ...start_cmd.start import start
from ...reused_functions import get_db_opts

def get_add_cmd():
    msg = """creates a container with mongodb installed 
    in order to act as a data base"""
    add = Command("add", description=msg)
    # ++++++++++++++++++++++++++++
    # name = _def_name_opt()
    # add.add_option(name)
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
    db = data_base.get_database()
    if db is not None: 
        msg = (" Ya existe una base de datos en la plataforma, " + 
                "no se permiten mas")
        add_logger.error(msg)
        return
    image = get_db_opts(options, flags)
    # if "--name" in options:
    #     name = options["--name"][0]
    db = data_base.create_database(image=image)
    if db is not None:
        program.list_lxc_containers() 
        msg = (f" Base de datos '{db}' inicializado\n")
        add_logger.info(msg)
        add_logger.info(" Estableciendo conexiones ...")
        platform.update_conexions()
        add_logger.info(" Conexiones establecidas\n")
        if "-l" in flags:
            start(args=[db.name], options=options, flags=flags)
    else:
        msg = (f" Fallo al crear ela base de datos")
        add_logger.error(msg)