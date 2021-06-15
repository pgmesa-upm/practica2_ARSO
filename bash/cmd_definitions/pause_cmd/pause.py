
from dependencies.cli.aux_classes import Command, Flag, Option
from ..reused_definitions import reused_opts, reused_flags

def get_pause_cmd():
    cmd_name = "pause"
    msg = """ 
    <void or container_names> pauses the containers currently 
    running, if void all containers are paused
    """
    pause = Command(
        cmd_name, description=msg, 
        extra_arg=True, multi=True
    )
    return pause