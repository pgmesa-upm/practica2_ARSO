
# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from .add_cmd.add import get_add_cmd, add
from .rm_cmd.rm import get_rm_cmd, rm

def get_database_cmd():
    msg = """allows to interact with the data base"""
    cmd_name = "database"
    database = Command(
        cmd_name, description=msg,
        mandatory_nested_cmd=True
    )
    # ++++++++++++++++++++++++++++
    add = get_add_cmd()
    database.nest_cmd(add)
    # ++++++++++++++++++++++++++++
    rm = get_rm_cmd()
    database.nest_cmd(rm)
    
    return database

# --------------------------------------------------------------------
# --------------------------------------------------------------------
def database(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={}):
    if "add" in nested_cmd:
        cmd_info = nested_cmd.pop("add")
        add(**cmd_info)
    elif "rm" in nested_cmd:
        cmd_info = nested_cmd.pop("rm")
        rm(**cmd_info)