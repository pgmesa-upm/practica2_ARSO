
# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from ....reused_definitions import reused_opts, reused_flags
# Imports para la funcion asociada al comando
from program import apps_handler as apps

def get_list_cmd():
    ls = Command(
        "list", description="lists the apps of repository"
    )
    return ls

# --------------------------------------------------------------------
# --------------------------------------------------------------------
def ls(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={}):
    apps.list_apps()