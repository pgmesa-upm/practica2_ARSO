
from dependencies.cli.aux_classes import Command, Flag, Option
from ...reused_definitions import reused_opts, reused_flags

def get_rm_cmd():
    msg = """removes the client"""
    rm = Command("rm", description=msg)
    # Flags ---------------------- 
    rm.add_flag(reused_flags["-y"])
    
    return rm
    
# --------------------------------------------------------------------
# --------------------------------------------------------------------
def rm():
    pass