
from dependencies.cli.aux_classes import Command, Flag, Option
from ....reused_definitions import reused_opts, reused_flags


def get_rm_cmd():
    msg = """<void or server_names> deletes the servers specified.
    If void all are deleted"""
    remove = Command(
        "rm", description=msg,
        extra_arg=True, multi=True
    )
    # ++++++++++++++++++++++++++++
    skip = reused_opts["--skip"]
    remove.add_option(skip)
    
    return remove