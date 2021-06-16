
from dependencies.cli.aux_classes import Command, Flag, Option
from .servs_cmd.servs import get_servs_cmd
from .client_cmd.client import get_client_cmd
from .loadbal_cmd.loadbal import get_loadbal_cmd

def get_machines_cmd():
    msg = """allows to interact with the different machines 
    of the platform"""
    cmd_name = "machns"
    machines = Command(
        cmd_name, description=msg,
        mandatory_nested_cmd=True
    )
    # ++++++++++++++++++++++++++++
    servs = get_servs_cmd()
    machines.nest_cmd(servs)
    # ++++++++++++++++++++++++++++
    client = get_client_cmd()
    machines.nest_cmd(client)
    # ++++++++++++++++++++++++++++
    loadbal = get_loadbal_cmd()
    machines.nest_cmd(loadbal)
    
    return machines

# --------------------------------------------------------------------
# --------------------------------------------------------------------
def machines():
    pass