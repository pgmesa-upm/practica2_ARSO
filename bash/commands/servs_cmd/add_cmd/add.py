
from dependencies.cli.aux_classes import Command, Flag, Option
from ...reused_definitions import reused_opts, reused_flags

def get_add_cmd():
    msg = """
    <void or number> creates the number of servers specified.
    If void, one is created"""
    add = Command(
        "add", description=msg,
        extra_arg=True, default=1, choices=[1,2,3,4,5]
    )
    # ++++++++++++++++++++++++++++
    name = reused_opts["--name"]
    add.add_option(name)
    # ++++++++++++++++++++++++++++
    image = _def_image_opt()
    add.add_option(image)
    # ++++++++++++++++++++++++++++
    use = _def_use_opt()
    add.add_option(use)
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

def _def_use_opt():
    msg = """ 
    <app_name> allows to specify the app that will be deployed
    in the servers (if they are being runned)
    """
    use = Option(
        "--use", description=msg, 
        extra_arg=True, mandatory=True
    )
    return use
    