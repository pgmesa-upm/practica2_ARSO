
import logging

# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from ...reused_definitions import reused_opts, reused_flags
# Imports para la funcion asociada al comando
from program.platform.machines import servers
from ...delete_cmd.delete import delete


def get_rm_cmd():
    msg = """<void or server_names> deletes the servers specified.
    If void all are deleted"""
    rm = Command(
        "rm", description=msg,
        extra_arg=True, multi=True
    )
    # ++++++++++++++++++++++++++++
    skip = reused_opts["--skip"]
    rm.add_option(skip)
    # Flags ---------------------- 
    rm.add_flag(reused_flags["-y"])
    
    return rm

# -------------------------------------------------------------------- 
# -------------------------------------------------------------------- 
def rm(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={}):
    delete(args=args, options=options, flags=flags, tags=[servers.TAG])