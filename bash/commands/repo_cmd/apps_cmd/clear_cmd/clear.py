
# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from ....reused_definitions import reused_opts, reused_flags
# Imports para la funcion asociada al comando
from program import apps_handler as apps
import copy

def get_clear_cmd():
    clear = Command(
        "clear", description="clears the apps repository"
    )
    # ++++++++++++++++++++++++++++
    skip = copy.deepcopy(reused_opts["--skip"])
    skip.description = """<names> skips the apps specified"""
    clear.add_option(skip)
    # Flags ---------------------- 
    clear.add_flag(reused_flags["-y"])
    
    return clear

# --------------------------------------------------------------------
# --------------------------------------------------------------------
def clear(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={}):
    skip = []
    if "--skip" in options:
        names = options["--skip"]
        for name in names: skip.append(name)
    if not "-y" in flags:
        msg = ("Se eliminaran todas las aplicaciones del " +
            "repositorio local")
        if "--skip" in options:
            msg += f", excepto {skip}"
        print(msg)
        answer = str(input("¿Estas seguro?(y/n): "))
        if answer.lower() != "y": return
        default = apps.get_defaultapp()
        if default not in skip:
            answer = str(input(
                f"¿Eliminar tambien default ({default})?(y/n): "
            ))
            if answer.lower() != "y": skip.append(apps.get_defaultapp())
    apps.clear_repository(skip=skip)