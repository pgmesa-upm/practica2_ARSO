

# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from ...reused_definitions import reused_opts, reused_flags
from .add_cmd.add import get_add_cmd, add
from .rm_cmd.rm import get_rm_cmd, rm
from .setdef_cmd.setdef import get_setdef_cmd, setdef
from .unsetdef_cmd.unsetdef import get_unsetdef_cmd, unsetdef
from .list_cmd.list import get_list_cmd, ls
from .clear_cmd.clear import get_clear_cmd, clear

# --------------------------------------------------------------------
def get_apps_cmd():
    msg = """allows to interact with the apps local repository"""
    apps = Command(
        "apps", description=msg,
        mandatory_nested_cmd=True
    )
    # ++++++++++++++++++++++++++++
    add  = get_add_cmd()
    apps.nest_cmd(add)
    # ++++++++++++++++++++++++++++
    rm = get_rm_cmd()
    apps.nest_cmd(rm)
    # ++++++++++++++++++++++++++++
    setdef = get_setdef_cmd()
    apps.nest_cmd(setdef)
    # ++++++++++++++++++++++++++++
    unsetdef = get_unsetdef_cmd()
    apps.nest_cmd(unsetdef)
    # ++++++++++++++++++++++++++++
    ls = get_list_cmd()
    apps.nest_cmd(ls)
    # ++++++++++++++++++++++++++++
    clear = get_clear_cmd()
    apps.nest_cmd(clear)
    
    return apps

# --------------------------------------------------------------------
# --------------------------------------------------------------------       
def apps(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={}):
    if "add" in nested_cmd:
        cmd_info = nested_cmd.pop("add")
        add(**cmd_info)
    elif "rm" in nested_cmd:
        cmd_info = nested_cmd.pop("rm")
        rm(**cmd_info)
    elif "setdef" in nested_cmd:
        cmd_info = nested_cmd.pop("setdef")
        setdef(**cmd_info)
    elif "unsetdef" in nested_cmd:
        cmd_info = nested_cmd.pop("unsetdef")
        unsetdef(**cmd_info)
    elif "list" in nested_cmd:
        cmd_info = nested_cmd.pop("list")
        ls(**cmd_info)
    elif "clear" in nested_cmd:
        cmd_info = nested_cmd.pop("clear")
        clear(**cmd_info)