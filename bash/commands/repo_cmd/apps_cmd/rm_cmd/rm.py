
# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from ....reused_definitions import reused_opts, reused_flags
# Imports para la funcion asociada al comando
from program import apps_handler as apps

def get_rm_cmd():
    msg = """<app_names> removes apps from the local repository"""
    rm = Command(
        "rm", description=msg, 
        extra_arg=True, mandatory=True, multi=True
    )
    # Flags ---------------------- 
    rm.add_flag(reused_flags["-y"])
    
    return rm

# --------------------------------------------------------------------
# --------------------------------------------------------------------
def rm(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={}):
    app_names = args
    if not "-y" in flags:
        default = apps.get_defaultapp()
        if default in app_names:
            print(f"La app '{default}' esta establecida como " + 
                "default")
            question = "¿Eliminar la app de todas formas?(y/n): "
            answer = str(input(question))
            if answer.lower() != "y": return
    for app in app_names: 
        apps.remove_app(app)