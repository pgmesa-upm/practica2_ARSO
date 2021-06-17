
from dependencies.cli.aux_classes import Command, Flag, Option
from ....reused_definitions import reused_opts, reused_flags

def get_clear_cmd():
    clear = Command(
        "clear", description="clears the apps repository"
    )
    # Flags ---------------------- 
    clear.add_flag(reused_flags["-y"])
    
    return clear

# --------------------------------------------------------------------
# --------------------------------------------------------------------
def clear(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={}):
    pass