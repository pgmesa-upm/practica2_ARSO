
from dependencies.cli.aux_classes import Command, Flag, Option
from ....reused_definitions import reused_opts, reused_flags

def get_algorithm_cmd():
    msg = """<algorithm_name> changes the balance algorithm"""
    algorithm = Command(
        "algorithm", description=msg, 
        extra_arg=True, mandatory=True
    )
    return algorithm

# --------------------------------------------------------------------
# --------------------------------------------------------------------
def algorithm():
    pass