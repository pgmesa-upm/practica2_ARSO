
from dependencies.cli.aux_classes import Command, Flag, Option
from ..reused_definitions import reused_opts, reused_flags

# --------------------------------------------------------------------
def get_servs_cmd():
    msg = """allows to interact with the servers"""
    cmd_name = "servs"
    servs = Command(
        cmd_name, description=msg,
        mandatory_opt=True
    )
    # ++++++++++++++++++++++++++++
    run = _def_run_opt()
    servs.add_option(run)
    # ++++++++++++++++++++++++++++
    stop = _def_stop_opt()
    servs.add_option(stop)
    # ++++++++++++++++++++++++++++
    pause = _def_pause_opt()
    servs.add_option(pause)
    # ++++++++++++++++++++++++++++
    add = _def_add_opt()
    servs.add_option(add)
    # ++++++++++++++++++++++++++++
    remove = _def_remove_opt()
    servs.add_option(remove)
    # ++++++++++++++++++++++++++++
    mark = _def_mark_opt()
    servs.add_option(mark)
    # ++++++++++++++++++++++++++++
    unmark = _def_unmark_opt()
    servs.add_option(unmark)
    # ++++++++++++++++++++++++++++
    use = _def_use_opt()
    servs.add_option(use)
    
    return servs

# --------------------------------------------------------------------
# --------------------------------------------------------------------    
def _def_run_opt():
    msg = """
    <void or server_name> starts the servers specified.
    If void, all of them
    """
    run = Command(
        "run", description=msg, 
        extra_arg=True, multi=True
    )
    run.add_option(reused_opts["--skip"])
    run.add_flag(reused_flags["-l"])
    return run
 
# --------------------------------------------------------------------   
def _def_stop_opt():
    msg = """
    <void or server_name> stops the servers specified.
    If void, all of them
    """
    stop = Command(
        "stop", description=msg,
        extra_arg=True, multi=True
    )
    stop.add_option(reused_opts["--skip"])
    return stop

# --------------------------------------------------------------------
def _def_pause_opt():
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
def _def_add_opt():
    msg = """
    <void or number> creates the number of servers specified.
    If void, one is created"""
    add = Command(
        "add", description=msg,
        extra_arg=True, default=1, choices=[1,2,3,4,5]
    )
    name = reused_opts["--name"]
    add.add_option(name)
    add.define_option(
        "--image", description="allows to specify the image",
        extra_arg=True, mandatory=True, multi=True
    )
    return add

# --------------------------------------------------------------------
def _def_remove_opt():
    msg = """<server_names> deletes the servers specified"""
    remove = Command(
        "rm", description=msg,
        extra_arg=True, mandatory=True, multi=True
    )
    return remove

# --------------------------------------------------------------------
def _def_mark_opt():
    msg = """
    <void or server_name> marks the app index.html of the 
    servers specified. If void, all of them
    """
    mark = Option(
        "mark", description=msg,
        extra_arg=True, multi=True
    )
    mark.add_option(reused_opts["--skip"])
    return mark

# --------------------------------------------------------------------
def _def_unmark_opt():
    msg = """
    <void or server_name> unmarks the app index.html of the 
    servers specified. If void, all of them
    """
    unmark = Option(
        "unmark", description=msg,
        extra_arg=True, multi=True
    )
    unmark.add_option(reused_opts["--skip"])
    return unmark

# --------------------------------------------------------------------
def _def_use_opt():
    msg = """
    <app_name> changes the app of the servers
    """
    use = Option(
        "use", description=msg, 
        extra_arg=True, mandatory=True
    )
    use.define_option(
        "--on", description="<names> allows to specify the servers", 
        extra_arg=True, mandatory=True, multi=True)
    return use
# --------------------------------------------------------------------