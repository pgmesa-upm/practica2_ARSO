
import logging

# Imports para la definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from ..reused_definitions import reused_opts, reused_flags
# Imports para la funcion asociada al comando
from program import program
from ..reused_functions import target_containers
from dependencies.utils.tools import concat_array
from program.controllers import bridges, containers


def get_stop_cmd():
    cmd_name = "stop"
    msg = """ 
    <void or container_names> stops the containers currently 
    running, if void all containers are stopped
    """
    stop = Command(
        cmd_name, description=msg, 
        extra_arg=True, multi=True
    )
    return stop

# --------------------------------------------------------------------
stop_logger = logging.getLogger(__name__)
@target_containers(stop_logger) 
def stop(*target_cs, options={}, flags=[]):
    """Detiene los contenedores que se enceuntren en target_cs

    Args:
        options (dict, optional): Opciones del comando parar
        flags (list, optional): Flags introducidos en el programa
    """
    # Paramos los contenedores validos
    msg = f" Deteniendo contenedores '{concat_array(target_cs)}'..."
    stop_logger.info(msg)
    succesful_cs = containers.stop(*target_cs)
    if not "-q" in flags:
        program.list_lxc_containers()
    cs_s = concat_array(succesful_cs)
    msg = (f" Los contenedores '{cs_s}' han sido detenidos \n")
    stop_logger.info(msg)