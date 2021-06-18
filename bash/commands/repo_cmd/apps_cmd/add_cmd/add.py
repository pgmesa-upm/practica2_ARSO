
# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from ....reused_definitions import reused_opts, reused_flags
# Imports para la funcion asociada al comando
from program import apps_handler as apps
from ..setdef_cmd.setdef import setdef

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
    # Flags ---------------------- 
    add.add_flag(Flag(
        "-d", description="sets the first app specified as default"
    ))
    
    return add


# --------------------------------------------------------------------
# --------------------------------------------------------------------
def add(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={}):
    names = []
    if "--name" in options:
        names = options["--name"]
    dif = len(args) - len(names)
    if dif > 0: 
        for _ in range(dif): names.append(None)
    for arg, name in zip(args, names):
        apps.add_app(arg, with_name=name)
    if "-d" in flags:
        setdef(args=[names[0]])