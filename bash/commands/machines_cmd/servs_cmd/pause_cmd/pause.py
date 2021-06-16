
from dependencies.cli.aux_classes import Command, Flag, Option
from ....reused_definitions import reused_opts, reused_flags

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