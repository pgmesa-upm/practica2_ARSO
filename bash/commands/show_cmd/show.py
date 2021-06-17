
# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from .state_cmd.state import get_state_cmd
from .dep_cmd.dep import get_dep_cmd
from .info_cmd.info import get_info_cmd, info
from .diagram_cmd.diagram import get_diagram_cmd

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
def show():
    pass