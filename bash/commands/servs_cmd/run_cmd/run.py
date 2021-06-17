
import logging

# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from ...reused_definitions import reused_opts, reused_flags
# Imports para la funcion asociada al comando
from program.platform.machines import servers
from ...start_cmd.start import start

def get_run_cmd():
    msg = """
    <void or server_name> starts the servers specified.
    If void, all of them
    """
    run = Command(
        "run", description=msg, 
        extra_arg=True, multi=True
    )
    # ++++++++++++++++++++++++++++
    skip = reused_opts["--skip"]
    run.add_option(skip)
    # ++++++++++++++++++++++++++++
    use = _def_use_opt()
    run.add_option(use)
    # Flags ----------------------
    run.add_flag(reused_flags["-m"])
    run.add_flag(reused_flags["-t"])
    return run

# --------------------------------------------------------------------
# --------------------------------------------------------------------
def _def_use_opt():
    msg = """ 
    <app_name> allows to specify the app that will be deployed
    in the servers
    """
    use = Option(
        "--use", description=msg, 
        extra_arg=True, mandatory=True
    )
    return use

# -------------------------------------------------------------------- 
# -------------------------------------------------------------------- 
def run(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={}):
    start(args=args, options=options, flags=flags, tags=[servers.TAG])