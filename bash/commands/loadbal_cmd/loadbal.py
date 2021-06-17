
# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from .set_cmd.set import get_set_cmd

def get_loadbal_cmd():
    msg = """allows to interact with the load balancer"""
    cmd_name = "loadbal"
    loadbal = Command(
        cmd_name, description=msg,
        mandatory_nested_cmd=True
    )
    # ++++++++++++++++++++++++++++
    set_ = get_set_cmd()
    loadbal.nest_cmd(set_)
    
    return loadbal

# --------------------------------------------------------------------
# --------------------------------------------------------------------
def loadbal():
    pass