
from dependencies.cli.aux_classes import Command, Flag, Option
from ...reused_definitions import reused_opts, reused_flags

def get_add_cmd():
    msg = """creates a container with lynx installed 
    in order to act as a client"""
    add = Command("add", description=msg)
    # ++++++++++++++++++++++++++++
    name = reused_opts["--name"]
    add.add_option(name)
    # ++++++++++++++++++++++++++++
    image = _def_image_opt()
    add.add_option(image)
    # Flags ----------------------
    add.add_flag(reused_flags["-l"])
    add.add_flag(reused_flags["-m"])
    add.add_flag(reused_flags["-t"])
    
    return add

def _def_image_opt():
    image = Option(
        "--image", description="allows to specify the image",
        extra_arg=True, mandatory=True, multi=True
    )
    return image
    
# --------------------------------------------------------------------
# --------------------------------------------------------------------
def add():
    pass