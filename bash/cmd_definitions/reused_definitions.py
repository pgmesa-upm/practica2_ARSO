
from dependencies.cli.aux_classes import Command, Option, Flag

reused_opts = {}

def def_reused_definitions():
    _def_reused_options()

def _def_reused_options():
    global reused_opts
    
    msg = """<names> skips the containers specified"""
    skip = Option(
        "--skip", description=msg,
        extra_arg=True, mandatory=True, multi=True
    )
    reused_opts["--skip"] = skip
    # -------------
    msg = """<names> allows to specify the names"""
    name = Option(
        "--name", description=msg,
        extra_arg=True, mandatory=True, multi=True
    )
    reused_opts["--name"] = name