from dependencies.cli.aux_classes import Command, Flag, Option
from ..reused_definitions import reused_opts, reused_flags

def get_delete_cmd():
    cmd_name = "delete"
    msg = """ 
    <void or container_names> deletes the containers 
    specified, if void all containers are deleted (some 
    may not be removable)
    """
    delete = Command(
        cmd_name, description=msg, 
        extra_arg=True,  multi=True
    )
    return delete