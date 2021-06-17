
# Imports para definicion del comando
import logging
from dependencies.cli.aux_classes import Command, Flag, Option
# Imports para la funcion asociada al comando
from ..reused_functions import get_cs
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
def term(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={},
         **extras):
    """Abre la terminal los contenedores que se enceuntren en 
    target_cs

    Args:
        options (dict, optional): Opciones del comando term
        flags (list, optional): Flags introducidos en el programa
    """
    # Arrancamos los contenedores validos
    tags = []
    if "tags" in extras: tags = extras["tags"]
    target_cs = get_cs(args, options, tags=tags)
    if target_cs is None: return
    cs_s = concat_array(target_cs)
    msg = f" Abriendo terminales de contenedores '{cs_s}'..."
    term_logger.info(msg)
    succesful_cs = containers.open_terminal(*target_cs)
    cs_s = concat_array(succesful_cs)
    msg = f" Se ha abierto la terminal de los contenedores '{cs_s}'\n"
    term_logger.info(msg)