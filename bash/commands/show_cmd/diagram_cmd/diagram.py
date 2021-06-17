
# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option

# --------------------------------------------------------------------
def get_diagram_cmd():
    msg = """
    displays a diagram that explains the structure of the platform
    """
    diagram = Command("diagram", description=msg)
    return diagram

# --------------------------------------------------------------------
# --------------------------------------------------------------------
def diagram():
    pass