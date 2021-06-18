
import logging

# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from ...reused_definitions import reused_opts, reused_flags
# Imports para la funcion asociada al comando
from program.platform.machines import load_balancer
from ...delete_cmd.delete import delete

def get_rm_cmd():
    msg = """removes the load balancer"""
    rm = Command("rm", description=msg)
    # Flags ---------------------- 
    rm.add_flag(reused_flags["-y"])
    
    return rm
    
# --------------------------------------------------------------------
# --------------------------------------------------------------------
rm_logger = logging.getLogger(__name__)
def rm(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={}):
    lb = load_balancer.get_lb()
    if lb is None: 
        msg = (" No existe el balanceador en la plataforma")
        rm_logger.error(msg)
        return
    delete(args=[lb.name], options=options, flags=flags)
    