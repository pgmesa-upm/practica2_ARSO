
# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from ...reused_definitions import reused_opts, reused_flags
# Imports para la funcion asociada al comando
from program.platform.machines import load_balancer

def get_reset_cmd():
    msg = """resets the configuration to the default one"""
    reset = Command("reset", description=msg)
    return reset

# --------------------------------------------------------------------
# --------------------------------------------------------------------
def reset(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={}):
    load_balancer.reset_config()