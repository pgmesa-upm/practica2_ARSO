

# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from ...reused_definitions import reused_opts, reused_flags
from .add_cmd.add import get_add_cmd
from .rm_cmd.rm import get_rm_cmd
from .setdef_cmd.setdef import get_setdef_cmd
from .unsetdef_cmd.unsetdef import get_unsetdef_cmd
from .list_cmd.list import get_list_cmd
from .clear_cmd.clear import get_clear_cmd
# Imports para la funcion asociada al comando
from program import apps_handler as apps_h

# --------------------------------------------------------------------
def get_apps_cmd():
    msg = """allows to interact with the apps local repository"""
    apps = Command(
        "apps", description=msg,
        mandatory_nested_cmd=True
    )
    # ++++++++++++++++++++++++++++
    add  = get_add_cmd()
    apps.nest_cmd(add)
    # ++++++++++++++++++++++++++++
    rm = get_rm_cmd()
    apps.nest_cmd(rm)
    # ++++++++++++++++++++++++++++
    setdef = get_setdef_cmd()
    apps.nest_cmd(setdef)
    # ++++++++++++++++++++++++++++
    unsetdef = get_unsetdef_cmd()
    apps.nest_cmd(unsetdef)
    # ++++++++++++++++++++++++++++
    ls = get_list_cmd()
    apps.nest_cmd(ls)
    # ++++++++++++++++++++++++++++-
    clear = get_clear_cmd()
    apps.nest_cmd(clear)
    
    return apps

# --------------------------------------------------------------------
# --------------------------------------------------------------------       
def apps(options={}, flags={}):
    if "markservs" in options:
        apps_h.mark_apps(*options["markservs"]["args"])
    elif "unmarkservs" in options:
        apps_h.mark_apps(*options["unmarkservs"]["args"], undo=True)
    elif "add" in options:
        apps_h.add_apps(*options["add"]["args"])
    elif "use" in options:
        servs = []
        if "--on" in options["use"]["options"]:
            servs = options["use"]["options"]["--on"]["args"]
        apps_h.use_app(options["use"]["args"][0], *servs)
        if "-m" in flags:
            apps_h.mark_apps()
    elif "setdef" in options:
        apps_h.set_default(options["setdef"]["args"][0])
    elif "unsetdef" in options:
        apps_h.unset_default()
    elif "list" in options:
        apps_h.list_apps()
    elif "rm" in options:
        app_names = options["rm"]["args"]
        if not "-y" in flags:
            default = apps_h.get_defaultapp()
            if default in app_names:
                print(f"La app '{default}' esta establecida como " + 
                    "default")
                question = "¿Eliminar la app de todas formas?(y/n): "
                answer = str(input(question))
                if answer.lower() != "y": return
        apps_h.remove_apps(*app_names)
    elif "emptyrep" in options:
        skip = []
        if not "-y" in flags:
            msg = ("Se eliminaran todas las aplicaciones del " +
                "repositorio local")
            print(msg)
            answer = str(input("¿Estas seguro?(y/n): "))
            if answer.lower() != "y": return
            answer = str(input("¿Eliminar tambien default?(y/n): "))
            if answer.lower() != "y": skip = [apps_h.get_defaultapp()]
        apps_h.clear_repository(skip=skip)