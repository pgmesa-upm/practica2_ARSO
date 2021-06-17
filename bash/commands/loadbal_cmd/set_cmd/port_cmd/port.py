
from dependencies.cli.aux_classes import Command, Flag, Option
from ....reused_definitions import reused_opts, reused_flags

def get_port_cmd():
    msg = """<port_number> changes the port where the load balancer
    is listening"""
    port = Command(
        "port", description=msg, 
        extra_arg=True, mandatory=True
    )
    return port

# --------------------------------------------------------------------
# --------------------------------------------------------------------
def port():
    pass