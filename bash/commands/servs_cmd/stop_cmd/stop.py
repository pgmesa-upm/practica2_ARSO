
import logging

# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from ...reused_definitions import reused_opts, reused_flags
# Imports para la funcion asociada al comando
from program.platform.machines import servers
from ...stop_cmd.stop import stop as stop_cs

def get_stop_cmd():
    msg = """
    <void or server_name> stops the servers specified.
    If void, all of them
    """
    stop = Command(
        "stop", description=msg,
        extra_arg=True, multi=True
    )
    # ++++++++++++++++++++++++++++
    skip = reused_opts["--skip"]
    stop.add_option(skip)
    
    return stop

# -------------------------------------------------------------------- 
# -------------------------------------------------------------------- 
def stop(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={}):
    stop_cs(args=args, options=options, flags=flags, tags=[servers.TAG])