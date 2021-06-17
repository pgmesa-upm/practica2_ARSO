
from dependencies.cli.aux_classes import Command, Option, Flag

reused_opts = {}; reused_flags = {}

def def_reused_definitions():
    _def_reused_options()
    _def_reused_flags()

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

def _def_reused_flags():
    global reused_flags
    
    msg = """ 
    launches the containers
    """
    launch = Flag("-l", description=msg)
    reused_flags[launch.name] = launch
    # -------------
    msg = """ 
    executes the action without asking confirmation
    """
    force = Flag("-y", description=msg)
    reused_flags[force.name] = force
    # -------------
    msg = """
    opens the terminal window of the containers
    """
    terminal = Flag("-t", description=msg)
    reused_flags[terminal.name] = terminal
    # -------------
    msg = """marks the servers index.html"""
    mark = Flag("-m", description=msg)
    reused_flags[mark.name] = mark
    