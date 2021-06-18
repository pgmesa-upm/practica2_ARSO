
# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from ....reused_definitions import reused_opts, reused_flags
# Imports para la funcion asociada al comando
from program import apps_handler as apps

def get_setdef_cmd():
    msg = """
    <app_name> changes the default app of the servers"""
    setdef = Command(
        "setdef", description=msg, 
        extra_arg=True, mandatory=True
    )
    return setdef

# --------------------------------------------------------------------
# --------------------------------------------------------------------
def setdef(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={}):
    apps.set_default(args[0])