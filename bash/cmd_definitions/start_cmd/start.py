
from dependencies.cli.aux_classes import Command, Flag, Option
from ..reused_definitions import reused_opts, reused_flags

def get_start_cmd():
    cmd_name = "start"
    msg = """ 
    <void or container_names> runs the containers specified, if 
    void all containers are runned
    """
    start = Command(
        cmd_name, description=msg, 
        extra_arg=True, multi=True
    )
    return start