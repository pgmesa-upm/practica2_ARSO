
from dependencies.cli.aux_classes import Command, Flag, Option
from ....reused_definitions import reused_opts, reused_flags

def get_setdef_cmd():
    msg = """
    <app_name> changes the default app of the servers"""
    setdef = Command(
        "setdef", description=msg, 
        extra_arg=True, mandatory=True
    )
    return setdef