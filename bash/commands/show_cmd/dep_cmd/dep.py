


# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option

# --------------------------------------------------------------------
def get_dep_cmd():
    msg = """
    shows information about the external dependencies of the program
    """
    dep = Command("dep", description=msg)
    return dep
# --------------------------------------------------------------------
# --------------------------------------------------------------------
def dep():
    pass