
# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from .run_cmd.run import get_run_cmd, run
from .stop_cmd.stop import get_stop_cmd, stop
from .pause_cmd.pause import get_pause_cmd, pause
from .add_cmd.add import get_add_cmd, add
from .rm_cmd.rm import get_rm_cmd, rm
from .mark_cmd.mark import get_mark_cmd, mark
from .unmark_cmd.unmark import get_unmark_cmd, unmark
from .use_cmd.use import get_use_cmd, use


# --------------------------------------------------------------------
def get_servs_cmd():
    msg = """allows to interact with the servers"""
    cmd_name = "servs"
    servs = Command(
        cmd_name, description=msg,
        mandatory_nested_cmd=True
    )
    # ++++++++++++++++++++++++++++
    run = get_run_cmd()
    servs.nest_cmd(run)
    # ++++++++++++++++++++++++++++
    stop = get_stop_cmd()
    servs.nest_cmd(stop)
    # ++++++++++++++++++++++++++++
    pause = get_pause_cmd()
    servs.nest_cmd(pause)
    # ++++++++++++++++++++++++++++
    add = get_add_cmd()
    servs.nest_cmd(add)
    # ++++++++++++++++++++++++++++
    remove = get_rm_cmd()
    servs.nest_cmd(remove)
    # ++++++++++++++++++++++++++++
    use = get_use_cmd()
    servs.nest_cmd(use)
    # ++++++++++++++++++++++++++++
    mark = get_mark_cmd()
    servs.nest_cmd(mark)
    # ++++++++++++++++++++++++++++
    unmark = get_unmark_cmd()
    servs.nest_cmd(unmark)
    
    return servs

# --------------------------------------------------------------------
# --------------------------------------------------------------------
def servs(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={}):
    if "run" in nested_cmd:
        cmd_info = nested_cmd.pop("run")
        run(**cmd_info)
    elif "stop" in nested_cmd:
        cmd_info = nested_cmd.pop("stop")
        stop(**cmd_info)
    elif "pause" in nested_cmd:
        cmd_info = nested_cmd.pop("pause")
        pause(**cmd_info) 
    elif "add" in nested_cmd:
        cmd_info = nested_cmd.pop("add")
        add(**cmd_info)
    elif "rm" in nested_cmd:
        cmd_info = nested_cmd.pop("rm")
        rm(**cmd_info)
    elif "use" in nested_cmd:
        cmd_info = nested_cmd.pop("use")
        use(**cmd_info)
    elif "mark" in nested_cmd:
        cmd_info = nested_cmd.pop("mark")
        mark(**cmd_info)
    elif "unmark" in nested_cmd:
        cmd_info = nested_cmd.pop("unmark")
        unmark(**cmd_info)
    
    

