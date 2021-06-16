
from dependencies.cli.aux_classes import Command, Flag, Option
from ....reused_definitions import reused_opts, reused_flags

def get_unmark_cmd():
    msg = """
    <void or server_name> unmarks the app index.html of the 
    servers specified. If void, all of them
    """
    unmark = Command(
        "unmark", description=msg,
        extra_arg=True, multi=True
    )
    # ++++++++++++++++++++++++++++
    skip = reused_opts["--skip"]
    unmark.add_option(skip)
    return unmark