
from dependencies.cli.aux_classes import Command, Flag, Option
from ....reused_definitions import reused_opts, reused_flags

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