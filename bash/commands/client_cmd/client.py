
# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from .add_cmd.add import get_add_cmd
from .rm_cmd.rm import get_rm_cmd

def get_client_cmd():
    msg = """allows to interact with the client"""
    cmd_name = "client"
    client = Command(
        cmd_name, description=msg,
        mandatory_nested_cmd=True
    )
    # ++++++++++++++++++++++++++++
    add = get_add_cmd()
    client.nest_cmd(add)
    # ++++++++++++++++++++++++++++
    rm = get_rm_cmd()
    client.nest_cmd(rm)
    
    return client

# --------------------------------------------------------------------
# --------------------------------------------------------------------
def client():
    pass