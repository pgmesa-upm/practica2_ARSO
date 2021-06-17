
# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
# Imports para la funcion asociada al comando
from program.platform import platform

# --------------------------------------------------------------------
def get_state_cmd():
    msg = """
    shows information about every machine/component of the platform
    """
    state = Command("state", description=msg)
    return state

# --------------------------------------------------------------------
# --------------------------------------------------------------------
def state(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={}):
    platform.print_state()