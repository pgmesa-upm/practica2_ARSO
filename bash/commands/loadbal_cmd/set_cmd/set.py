
# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from ...reused_definitions import reused_opts, reused_flags
# Imports para la funcion asociada al comando
from .algorithm_cmd.algorithm import get_algorithm_cmd, algorithm
from .port_cmd.port import get_port_cmd, port

def get_set_cmd():
    msg = """allows to change some varibales"""
    set_ = Command(
        "set", description=msg, 
        mandatory_nested_cmd=True
    )
    # ++++++++++++++++++++++++++++
    algorithm = get_algorithm_cmd()
    set_.nest_cmd(algorithm)
    # ++++++++++++++++++++++++++++
    port = get_port_cmd()
    set_.nest_cmd(port)
    
    return set_

# --------------------------------------------------------------------
# --------------------------------------------------------------------
def set_(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={}):
    if "algorithm" in nested_cmd:
        cmd_info = nested_cmd.pop("algorithm")
        algorithm(**cmd_info)
    elif "port" in nested_cmd:
        cmd_info = nested_cmd.pop("port")
        port(**cmd_info)