
# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from .set_cmd.set import get_set_cmd
# Imports para la funcion asociada al comando
from .add_cmd.add import get_add_cmd, add
from .rm_cmd.rm import get_rm_cmd, rm
from .set_cmd.set import get_set_cmd, set_
from .reset_cmd.reset import get_reset_cmd, reset

def get_loadbal_cmd():
    msg = """allows to interact with the load balancer"""
    cmd_name = "loadbal"
    loadbal = Command(
        cmd_name, description=msg,
        mandatory_nested_cmd=True
    )
    # ++++++++++++++++++++++++++++
    add = get_add_cmd()
    loadbal.nest_cmd(add)
    # ++++++++++++++++++++++++++++
    rm = get_rm_cmd()
    loadbal.nest_cmd(rm)
    # ++++++++++++++++++++++++++++
    set_ = get_set_cmd()
    loadbal.nest_cmd(set_)
    # ++++++++++++++++++++++++++++
    reset = get_reset_cmd()
    loadbal.nest_cmd(reset)
    
    return loadbal

# --------------------------------------------------------------------
# --------------------------------------------------------------------
def loadbal(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={}):
    if "add" in nested_cmd:
        cmd_info = nested_cmd.pop("add")
        add(**cmd_info)
    elif "rm" in nested_cmd:
        cmd_info = nested_cmd.pop("rm")
        rm(**cmd_info)
    elif "set" in nested_cmd:
        cmd_info = nested_cmd.pop("set")
        set_(**cmd_info)
    elif "reset" in nested_cmd:
        cmd_info = nested_cmd.pop("reset")
        reset(**cmd_info)
        