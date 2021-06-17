
import logging

# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from ...reused_definitions import reused_opts, reused_flags
# Imports para la funcion asociada al comando
from program.platform.machines import servers
from ...pause_cmd.pause import pause as pause_cs

def get_pause_cmd():
    msg = """
    <void or server_name> pauses the servers specified.
    If void, all of them
    """
    pause = Command(
        "pause", description=msg,
        extra_arg=True, multi=True
    )
    pause.add_option(reused_opts["--skip"])
    return pause

# -------------------------------------------------------------------- 
# -------------------------------------------------------------------- 
def pause(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={}):
    pause_cs(args=args, options=options, flags=flags, tags=[servers.TAG])