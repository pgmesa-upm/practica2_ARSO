
from dependencies.cli.cli import Cli, CmdLineError
from dependencies.cli.aux_classes import Command, Flag, Option

from .commands.deploy_cmd.deploy import get_deploy_cmd, deploy
from .commands.start_cmd.start import get_start_cmd, start
from .commands.stop_cmd.stop import get_stop_cmd, stop
from .commands.pause_cmd.pause import get_pause_cmd, pause
from .commands.delete_cmd.delete import get_delete_cmd, delete
from .commands.destroy_cmd.destroy import get_destroy_cmd, destroy
from .commands.servs_cmd.servs import get_servs_cmd, servs
from .commands.client_cmd.client import get_client_cmd, client
from .commands.loadbal_cmd.loadbal import get_loadbal_cmd, loadbal
from .commands.database_cmd.database import get_database_cmd, database
from .commands.repo_cmd.repo import get_repo_cmd, repo
from .commands.show_cmd.show import get_show_cmd, show
from .commands.term_cmd.term import get_term_cmd, term
from .commands.publish_cmd.publish import get_publish_cmd, publish
from .commands.reused_definitions import def_reused_definitions

# --------------------------- BASH HANDLER ---------------------------
# --------------------------------------------------------------------
# Define todos los comandos que va a tener el programa y ejecuta las
# ordenes que introduzca el usuario por terminal
# --------------------------------------------------------------------

# En este diccionario se asocia a cada comando una funcion a ejecutar
_commands = {}
# --------------------------------------------------------------------
def execute(cmd_line:dict):
    """Ejecuta la funcion correspondiente al comando introducido por 
    el usuario

    Args:
        args (dict): Linea de comandos introducida por el usuario 
            ya validada, es decir, debe ser correcta
    """
    cmd_passed = cmd_line.pop("_cmd_")
    for cmd_name, func in _commands.items():
        if cmd_name == cmd_passed:
            cmd_info = cmd_line.pop(cmd_passed)
            func(**cmd_info)
            break
        
# --------------------------------------------------------------------
def config_cli() -> Cli:
    cli = Cli()
    def_reused_definitions()
    # DEPLOY +++++++++++++++++++++
    deploy_cmd = get_deploy_cmd(); cli.add_command(deploy_cmd)
    _commands[deploy_cmd.name] = deploy
    # START ++++++++++++++++++++++
    start_cmd = get_start_cmd(); cli.add_command(start_cmd)
    _commands[start_cmd.name] = start
    # STOP +++++++++++++++++++++++
    stop_cmd = get_stop_cmd(); cli.add_command(stop_cmd)
    _commands[stop_cmd.name] = stop
    # PAUSE ++++++++++++++++++++++
    pause_cmd = get_pause_cmd(); cli.add_command(pause_cmd)
    _commands[pause_cmd.name] = pause
    # DELETE +++++++++++++++++++++
    delete_cmd = get_delete_cmd(); cli.add_command(delete_cmd)
    _commands[delete_cmd.name] = delete
    # DESTROY ++++++++++++++++++++
    destroy_cmd = get_destroy_cmd(); cli.add_command(destroy_cmd)
    _commands[destroy_cmd.name] = destroy
    # SERVS ++++++++++++++++++++++
    servs_cmd = get_servs_cmd(); cli.add_command(servs_cmd)
    _commands[servs_cmd.name] = servs
    # CLIENT +++++++++++++++++++++
    client_cmd = get_client_cmd(); cli.add_command(client_cmd)
    _commands[client_cmd.name] = client
    # LOADBAL ++++++++++++++++++++
    lb_cmd = get_loadbal_cmd(); cli.add_command(lb_cmd)
    _commands[lb_cmd.name] = loadbal
    # DATABASE +++++++++++++++++++
    db_cmd = get_database_cmd(); cli.add_command(db_cmd)
    _commands[db_cmd.name] = database
    # REPO +++++++++++++++++++++++
    repo_cmd = get_repo_cmd(); cli.add_command(repo_cmd)
    _commands[repo_cmd.name] = repo
    # SHOW +++++++++++++++++++++++
    show_cmd = get_show_cmd(); cli.add_command(show_cmd)
    _commands[show_cmd.name] = show
    # TERM +++++++++++++++++++++++
    term_cmd = get_term_cmd(); cli.add_command(term_cmd)
    _commands[term_cmd.name] = term
    # PUBLISH ++++++++++++++++++++
    publish_cmd = get_publish_cmd(); cli.add_command(publish_cmd)
    _commands[publish_cmd.name] = publish
    # ---------------- Global Flags
    msg = """ 
    'warning mode', only shows warning and error msgs during 
    execution
    """
    verbosity = Flag(
        "-w", description=msg,notCompatibleWithFlags=["-d"]
    )
    cli.add_global_flag(verbosity)
    # -----------------------------
    msg = """ 
    'debug mode' option for debugging. Shows debug msgs during
    execution
    """
    debugging = Flag(
        "-d", description=msg, notCompatibleWithFlags=["-w"]
    )
    cli.add_global_flag(debugging)
    # -----------------------------
    msg = """ 
    'quiet mode', doesn't show any msg during execution (only 
    when an error occurs)
    """
    quiet = Flag(
        "-q", description=msg, notCompatibleWithFlags=["-w","-d"],
    )
    cli.add_global_flag(quiet)
    # -----------------------------
    msg = """ 
    executes the code sequencially instead of concurrently
    """
    sequential_execution = Flag("-s", description=msg)
    cli.add_global_flag(sequential_execution)
    
    return cli    
    
# --------------------------------------------------------------------