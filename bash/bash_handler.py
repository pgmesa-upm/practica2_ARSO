
from dependencies.cli.cli import Cli, CmdLineError
from dependencies.cli.aux_classes import Command, Flag, Option

from .commands.deploy_cmd.deploy import get_deploy_cmd, deploy
from .commands.start_cmd.start import get_start_cmd, start
from .commands.stop_cmd.stop import get_stop_cmd, stop
from .commands.pause_cmd.pause import get_pause_cmd, pause
from .commands.delete_cmd.delete import get_delete_cmd, delete
from .commands.destroy_cmd.destroy import get_destroy_cmd, destroy
from .commands.machines_cmd.machines import get_machines_cmd, machines
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
            func(*cmd_info.pop("args"), **cmd_info)
            break
        
# --------------------------------------------------------------------
def config_cli() -> Cli:
    cli = Cli()
    def_reused_definitions()
    # ++++++++++++++++++++++++++++
    deploy_cmd = get_deploy_cmd()
    cli.add_command(deploy_cmd)
    _commands[deploy_cmd.name] = deploy
    # ++++++++++++++++++++++++++++
    start_cmd = get_start_cmd()
    cli.add_command(start_cmd)
    _commands[start_cmd.name] = start
    # ++++++++++++++++++++++++++++
    stop_cmd = get_stop_cmd()
    cli.add_command(stop_cmd)
    _commands[stop_cmd.name] = stop
    # ++++++++++++++++++++++++++++
    pause_cmd = get_pause_cmd()
    cli.add_command(pause_cmd)
    _commands[pause_cmd.name] = pause
    # ++++++++++++++++++++++++++++
    delete_cmd = get_delete_cmd()
    cli.add_command(delete_cmd)
    _commands[delete_cmd.name] = delete
    # ++++++++++++++++++++++++++++
    destroy_cmd = get_destroy_cmd()
    cli.add_command(destroy_cmd)
    _commands[destroy_cmd.name] = destroy
    # ++++++++++++++++++++++++++++
    servs_cmd = get_machines_cmd()
    cli.add_command(servs_cmd)
    _commands[servs_cmd.name] = machines
    # ++++++++++++++++++++++++++++
    repo_cmd = get_repo_cmd()
    cli.add_command(repo_cmd)
    _commands[repo_cmd.name] = repo
    # ++++++++++++++++++++++++++++
    show_cmd = get_show_cmd()
    cli.add_command(show_cmd)
    _commands[show_cmd.name] = show
    # ++++++++++++++++++++++++++++
    term_cmd = get_term_cmd()
    cli.add_command(term_cmd)
    _commands[term_cmd.name] = term
    # ++++++++++++++++++++++++++++
    publish_cmd = get_publish_cmd()
    cli.add_command(publish_cmd)
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