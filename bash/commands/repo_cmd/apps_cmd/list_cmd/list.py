
from dependencies.cli.aux_classes import Command, Flag, Option
from ....reused_definitions import reused_opts, reused_flags

def get_list_cmd():
    ls = Command(
        "list", description="lists the apps of repository"
    )
    return ls

# --------------------------------------------------------------------
# --------------------------------------------------------------------
def ls(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={}):
    pass