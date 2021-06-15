

from dependencies.cli.aux_classes import Command, Flag, Option
from ..reused_definitions import reused_opts, reused_flags

def get_stop_cmd():
    cmd_name = "stop"
    msg = """ 
    <void or container_names> stops the containers currently 
    running, if void all containers are stopped
    """
    stop = Command(
        cmd_name, description=msg, 
        extra_arg=True, multi=True
    )
    return stop