
# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
# Imports para la funcion asociada al comando
from program.platform import platform

# --------------------------------------------------------------------
def get_state_cmd():
    msg = """ 
    <void or machine_names> shows information about every 
    machine/component of the platform specified, if void, all are showed
    """
    state = Command(
        "state", description=msg,
        extra_arg=True, multi=True
    )
    return state

# --------------------------------------------------------------------
# --------------------------------------------------------------------
def state(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={}):
    platform.print_state(machines=args)