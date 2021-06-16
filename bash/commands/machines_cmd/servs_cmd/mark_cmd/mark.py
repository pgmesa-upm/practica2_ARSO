
from dependencies.cli.aux_classes import Command, Flag, Option
from ....reused_definitions import reused_opts, reused_flags

def get_mark_cmd():
    msg = """
    <void or server_name> marks the app index.html of the 
    servers specified. If void, all of them
    """
    mark = Command(
        "mark", description=msg,
        extra_arg=True, multi=True
    )
    # ++++++++++++++++++++++++++++
    skip = reused_opts["--skip"]
    mark.add_option(skip)
    
    return mark