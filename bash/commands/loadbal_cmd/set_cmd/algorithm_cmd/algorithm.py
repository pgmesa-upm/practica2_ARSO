
# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from ....reused_definitions import reused_opts, reused_flags
# Imports para la funcion asociada al comando
from program.platform.machines import load_balancer

def get_algorithm_cmd():
    msg = """<algorithm_name> changes the balance algorithm. Some of the
    most common ones are 'roundrobin(default), leastconn, source ...'
    """
    algorithm = Command(
        "algorithm", description=msg, 
        extra_arg=True, mandatory=True
    )
    return algorithm

# --------------------------------------------------------------------
# --------------------------------------------------------------------
def algorithm(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={}):
    algorithm = args[0]
    load_balancer.change_algorithm(algorithm)