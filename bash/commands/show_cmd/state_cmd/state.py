
# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option

# --------------------------------------------------------------------
def get_state_cmd():
    msg = """
    shows information about every machine/component of the platform
    """
    state = Command("state", description=msg)
    return state

# --------------------------------------------------------------------
# --------------------------------------------------------------------
def state():
    pass