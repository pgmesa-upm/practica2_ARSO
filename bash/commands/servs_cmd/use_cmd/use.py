
# Imports para definicion del comando
from program.controllers import containers
from dependencies import register
from dependencies.cli.aux_classes import Command, Flag, Option
from ...reused_definitions import reused_opts, reused_flags
# Imports para la funcion asociada al comando
from program.apps_handler import use_app

def get_use_cmd():
    msg = """
    <app_name> changes the app of the servers
    """
    use = Command(
        "use", description=msg, 
        extra_arg=True, mandatory=True
    )
    # ++++++++++++++++++++++++++++
    on = _def_on_opt()
    use.add_option(on)
    
    return use

# --------------------------------------------------------------------
# --------------------------------------------------------------------
def _def_on_opt():
    on = Option(
        "--on", description="<names> allows to specify the servers", 
        extra_arg=True, mandatory=True, multi=True
    )
    return on

# -------------------------------------------------------------------- 
# -------------------------------------------------------------------- 
def use(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={}):
    app = args[0]
    serv_names = []
    if "--on" in options:
        serv_names = options["--on"]
    use_app(app, *serv_names)