
# Imports para definicion del comando
import logging
from dependencies.cli.aux_classes import Command, Flag, Option
# Imports para la funcion asociada al comando
from ..reused_functions import target_containers
from dependencies.utils.tools import concat_array
from program.controllers import bridges, containers


def get_term_cmd():
    cmd_name = "term"
    msg = """ 
    <void or container_names> opens the terminal of the containers 
    specified or all of them if no name is given
    """
    term = Command(
        cmd_name, description=msg, 
        extra_arg=True, multi=True
    )
    return term

# --------------------------------------------------------------------
# --------------------------------------------------------------------
term_logger = logging.getLogger(__name__)
@target_containers(term_logger) 
def term(*target_cs, options={}, flags=[]):
    """Abre la terminal los contenedores que se enceuntren en 
    target_cs

    Args:
        options (dict, optional): Opciones del comando term
        flags (list, optional): Flags introducidos en el programa
    """
    # Arrancamos los contenedores validos
    cs_s = concat_array(target_cs)
    msg = f" Abriendo terminales de contenedores '{cs_s}'..."
    term_logger.info(msg)
    succesful_cs = containers.open_terminal(*target_cs)
    cs_s = concat_array(succesful_cs)
    msg = f" Se ha abierto la terminal de los contenedores '{cs_s}'\n"
    term_logger.info(msg)