
from dependencies.cli.aux_classes import Command, Flag, Option
from ....reused_definitions import reused_opts, reused_flags

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