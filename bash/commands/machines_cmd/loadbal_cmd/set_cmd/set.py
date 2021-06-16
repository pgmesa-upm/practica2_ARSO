
from dependencies.cli.aux_classes import Command, Flag, Option
from ....reused_definitions import reused_opts, reused_flags
from .algorithm_cmd.algorithm import get_algorithm_cmd
from .port_cmd.port import get_port_cmd

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
def set_():
    pass