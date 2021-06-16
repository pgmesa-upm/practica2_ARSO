
# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from ..reused_definitions import reused_opts, reused_flags
from .run_cmd.run import get_run_cmd
from .stop_cmd.stop import get_stop_cmd
from .pause_cmd.pause import get_pause_cmd
from .add_cmd.add import get_add_cmd
from .rm_cmd.rm import get_rm_cmd
from .mark_cmd.mark import get_mark_cmd
from .unmark_cmd.unmark import get_unmark_cmd
from .use_cmd.use import get_use_cmd


# --------------------------------------------------------------------
def get_servs_cmd():
    msg = """allows to interact with the servers"""
    cmd_name = "servs"
    servs = Command(
        cmd_name, description=msg,
        mandatory_opt=True
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
    mark = get_mark_cmd()
    servs.nest_cmd(mark)
    # ++++++++++++++++++++++++++++
    unmark = get_unmark_cmd()
    servs.nest_cmd(unmark)
    # ++++++++++++++++++++++++++++
    use = get_use_cmd()
    servs.nest_cmd(use)
    
    return servs

# --------------------------------------------------------------------
# --------------------------------------------------------------------
def servs():
    pass

