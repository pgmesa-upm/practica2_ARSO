
# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from ....reused_definitions import reused_opts, reused_flags
# Imports para la funcion asociada al comando
from program import apps_handler as apps

def get_add_cmd():
    msg = """
    <absolute_paths> adds 1 or more apps to the local repository
    """
    add = Command(
        "add", description=msg, 
        extra_arg=True, mandatory=True, multi=True
    )
    # ++++++++++++++++++++++++++++
    name = reused_opts["--name"]
    add.add_option(name)
    
    return add


# --------------------------------------------------------------------
# --------------------------------------------------------------------
def add(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={}):
    if "--name" in options:
        pass
    apps.add_apps(*args)