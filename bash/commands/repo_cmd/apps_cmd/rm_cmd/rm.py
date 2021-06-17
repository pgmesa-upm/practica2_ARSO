
from dependencies.cli.aux_classes import Command, Flag, Option
from ....reused_definitions import reused_opts, reused_flags

def get_rm_cmd():
    msg = """<app_names> removes apps from the local repository"""
    rm = Command(
        "rm", description=msg, 
        extra_arg=True, mandatory=True, multi=True
    )
    # Flags ---------------------- 
    rm.add_flag(reused_flags["-y"])
    
    return rm

# --------------------------------------------------------------------
# --------------------------------------------------------------------
def rm(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={}):
    pass