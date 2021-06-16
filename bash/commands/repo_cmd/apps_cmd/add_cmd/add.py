
from dependencies.cli.aux_classes import Command, Flag, Option
from ....reused_definitions import reused_opts, reused_flags

def get_add_cmd():
    msg = """
    <absolute_paths> adds 1 or more apps to the local repository
    """
    add = Command(
        "add", description=msg, 
        extra_arg=True, mandatory=True, multi=True
    )
    # ++++++++++++++++++++++++++++
    name = reused_opts["--name"]
    add.add_option(name)
    
    return add