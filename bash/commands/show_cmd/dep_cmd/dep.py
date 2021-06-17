
# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
# Imports para la funcion asociada al comando
from program import program

# --------------------------------------------------------------------
def get_dep_cmd():
    msg = """
    shows information about the external dependencies of the program
    """
    dep = Command("dep", description=msg)
    return dep
# --------------------------------------------------------------------
# --------------------------------------------------------------------
def dep(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={}):
    program.show_dependencies()