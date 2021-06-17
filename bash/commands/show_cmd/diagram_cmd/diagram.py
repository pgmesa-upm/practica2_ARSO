
# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
# Imports para la funcion asociada al comando
from program import program


def get_diagram_cmd():
    msg = """
    displays a diagram that explains the structure of the platform
    """
    diagram = Command("diagram", description=msg)
    return diagram

# --------------------------------------------------------------------
# --------------------------------------------------------------------
def diagram(*args, options:dict={}, flags:dict={}, nested_cmds:dict={}):
    program.show_platform_diagram()