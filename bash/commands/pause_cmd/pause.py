
import logging

# Imports para la definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from ..reused_definitions import reused_opts, reused_flags
# Imports para la funcion asociada al comando
from program import program
from ..reused_functions import get_cs
from dependencies.utils.tools import concat_array
from program.controllers import bridges, containers


def get_pause_cmd():
    cmd_name = "pause"
    msg = """ 
    <void or container_names> pauses the containers currently 
    running, if void all containers are paused
    """
    pause = Command(
        cmd_name, description=msg, 
        extra_arg=True, multi=True
    )
    # ++++++++++++++++++++++++++++
    skip = reused_opts["--skip"]
    pause.add_option(skip)
    
    return pause

# --------------------------------------------------------------------
pause_logger = logging.getLogger(__name__) 
def pause(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={},
          **extras):
    """Pausa los contenedores que se enceuntren en target_cs

    Args:
        options (dict, optional): Opciones del comando pausar
        flags (list, optional): Flags introducidos en el programa
    """
    # Pausamos los contenedores validos
    tags = []
    if "tags" in extras: tags = extras["tags"]
    target_cs = get_cs(args, options, tags=tags)
    if target_cs is None: return
    msg = f" Pausando contenedores '{concat_array(target_cs)}'..."
    pause_logger.info(msg)
    successful_cs = containers.pause(*target_cs)
    program.list_lxc_containers(*successful_cs)
    cs_s = concat_array(successful_cs)
    msg = (f" Los contenedores '{cs_s}' han sido pausados \n")
    pause_logger.info(msg)