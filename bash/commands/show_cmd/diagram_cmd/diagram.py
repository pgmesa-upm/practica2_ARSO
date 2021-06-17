
# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
# Imports para la funcion asociada al comando
import logging
from program import program


def get_diagram_cmd():
    msg = """
    displays a diagram that explains the structure of the platform
    """
    diagram = Command("diagram", description=msg)
    return diagram

# --------------------------------------------------------------------
# --------------------------------------------------------------------
diagram_logger = logging.getLogger(__name__)
def diagram(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={}):
    diagram_logger.info(" Abriendo diagrama...")
    program.show_platform_diagram()