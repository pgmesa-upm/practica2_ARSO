
# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from ....reused_definitions import reused_opts, reused_flags
# Imports para la funcion asociada al comando
from program import apps_handler as apps

def get_unsetdef_cmd():
    msg = """makes the default app to be none"""
    unsetdef = Command("unsetdef", description=msg)
    return unsetdef

# --------------------------------------------------------------------
# --------------------------------------------------------------------
def unsetdef(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={}):
    apps.unset_default()