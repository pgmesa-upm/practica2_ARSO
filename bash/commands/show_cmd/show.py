
# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from .state_cmd.state import get_state_cmd, state
from .dep_cmd.dep import get_dep_cmd, dep
from .info_cmd.info import get_info_cmd, info
from .diagram_cmd.diagram import get_diagram_cmd, diagram

# --------------------------------------------------------------------
def get_show_cmd():
    msg = """shows information about the program"""
    show = Command(
        "show", description=msg,
        mandatory_nested_cmd=True
    )
    # ++++++++++++++++++++++++++++
    state = get_state_cmd()
    show.nest_cmd(state)
    # ++++++++++++++++++++++++++++
    diagram = get_diagram_cmd()
    show.nest_cmd(diagram)
    # ++++++++++++++++++++++++++++
    info = get_info_cmd()
    show.nest_cmd(info)
    # ++++++++++++++++++++++++++++
    dep = get_dep_cmd()
    show.nest_cmd(dep)
    
    return show

# --------------------------------------------------------------------
# --------------------------------------------------------------------
def show(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={}):
    """Muestra informacion sobre el programa

    Args:
        choice (str): Indica que informacion se quiere mostrar
        options (dict, optional): Opciones del comando show
        flags (list, optional): Flags introducidos en el programa
    """
    if "diagram" in nested_cmd:
        cmd_info = nested_cmd.pop("diagram")
        diagram(**cmd_info)
    elif "state" in nested_cmd:
        cmd_info = nested_cmd.pop("state")
        state(**cmd_info)
    elif "dep" in nested_cmd:
        cmd_info = nested_cmd.pop("dep")
        dep(**cmd_info)
    elif "info" in nested_cmd:
        cmd_info = nested_cmd.pop("info")
        info(**cmd_info)