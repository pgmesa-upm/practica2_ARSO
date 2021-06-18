
# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from ....reused_definitions import reused_opts, reused_flags
# Imports para la funcion asociada al comando
from program.platform.machines import load_balancer

def get_port_cmd():
    msg = """<port_number> changes the port where the load balancer
    is listening (default -> 80)"""
    port = Command(
        "port", description=msg, 
        extra_arg=True, mandatory=True
    )
    return port

# --------------------------------------------------------------------
# --------------------------------------------------------------------
def port(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={}):
    port = args[0]
    load_balancer.change_binded_port(port)