
import logging

# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from ...reused_definitions import reused_opts, reused_flags
# Imports para la funcion asociada al comando
from program.platform.machines import servers
from dependencies.utils.tools import concat_array
from ...reused_functions import get_cs


def get_unmark_cmd():
    msg = """
    <void or server_name> unmarks the app index.html of the 
    servers specified. If void, all of them
    """
    unmark = Command(
        "unmark", description=msg,
        extra_arg=True, multi=True
    )
    # ++++++++++++++++++++++++++++
    skip = reused_opts["--skip"]
    unmark.add_option(skip)
    
    return unmark

# -------------------------------------------------------------------- 
# -------------------------------------------------------------------- 
unmark_logger = logging.getLogger(__name__)
def unmark(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={}):
    servs = get_cs(args, options, tags=[servers.TAG])
    if servs is None: return
    unmark_logger.info(f" Desmarcando servidores '{concat_array(servs)}'...")
    for serv in servs:
        servers.mark_htmlindexes(serv, undo=True)