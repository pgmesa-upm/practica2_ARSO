

from dependencies.cli.aux_classes import Command, Flag, Option
from ..reused_definitions import reused_opts, reused_flags

def get_destroy_cmd():
    cmd_name = "destroy"
    msg = """ 
    deletes every component of the platform created
    """
    destroy = Command(cmd_name, description=msg)
    return destroy