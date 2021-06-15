
from program.controllers.containers import delete
import bash.cmd_functions.commands as commands_rep
from dependencies.cli.cli import Cli, CmdLineError
from dependencies.cli.aux_classes import Command, Flag, Option

from .cmd_definitions.deploy_cmd.deploy import get_deploy_cmd
from .cmd_definitions.start_cmd.start import get_start_cmd
from .cmd_definitions.stop_cmd.stop import get_stop_cmd
from .cmd_definitions.pause_cmd.pause import get_pause_cmd
from .cmd_definitions.delete_cmd.delete import get_delete_cmd
from .cmd_definitions.destroy_cmd.destroy import get_destroy_cmd
from .cmd_definitions.servs_cmd.servs import get_servs_cmd
from .cmd_definitions.repo_cmd.repo import get_repo_cmd


from .cmd_definitions.reused_definitions import def_reused_definitions
from .cmd_functions import commands as commands_rep

# --------------------------- BASH HANDLER ---------------------------
# --------------------------------------------------------------------
# Define todos los comandos que va a tener el programa y ejecuta las
# ordenes que introduzca el usuario por terminal
# --------------------------------------------------------------------

# En este diccionario se asocia a cada comando una funcion a ejecutar
_commands = {}
# Opciones reutilizadas por varios comandos
_reused_opts = {}
# --------------------------------------------------------------------
def execute(cmd_line:dict):
    """Ejecuta la funcion correspondiente al comando introducido por 
    el usuario

    Args:
        args (dict): Linea de comandos introducida por el usuario 
            ya validada, es decir, debe ser correcta
    """
    return
    for cmd_name, cmd in _commands.items():
        if cmd_name == cmd_line["cmd"]:
            args = cmd_line["args"]
            options = cmd_line["options"]
            flags = cmd_line["flags"]
            cmd(*args, options=options, flags=flags)
            break
        
# --------------------------------------------------------------------
def config_cli() -> Cli:
    cli = Cli()
    def_reused_definitions()
    # ++++++++++++++++++++++++++++
    deploy = get_deploy_cmd()
    cli.add_command(deploy)
    #_commands[deploy.name] = commands_rep.deploy
    # ++++++++++++++++++++++++++++
    start = get_start_cmd()
    cli.add_command(start)
    #_commands[start.name] = commands_rep.start
    # ++++++++++++++++++++++++++++
    stop = get_stop_cmd()
    cli.add_command(stop)
    #_commands[stop.name] = commands_rep.stop
    # ++++++++++++++++++++++++++++
    pause = get_pause_cmd()
    cli.add_command(pause)
    _commands[pause.name] = commands_rep.pause
    # ++++++++++++++++++++++++++++
    delete = get_delete_cmd()
    cli.add_command(delete)
    #_commands[delete.name] = commands_rep.delete
    # ++++++++++++++++++++++++++++
    destroy = get_destroy_cmd()
    cli.add_command(destroy)
    #_commands[destroy.name] = commands_rep.destroy
    # ++++++++++++++++++++++++++++
    servs = get_servs_cmd()
    cli.add_command(servs)
    #_commands[servs.name] = commands_rep.servs
    # ++++++++++++++++++++++++++++
    repo = get_repo_cmd()
    cli.add_command(repo)
    # _commands[servs.name] = commands_rep.servs
    # ++++++++++++++++++++++++++++
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








def _def_platform_cmds(cli:Cli):
    global _commands
    
    # ++++++++++++++++++++++++++++
    cmd_name = "show"
    msg = """ 
    shows information about the program
    """
    msg = ""
    show = Command(
        cmd_name, description=msg, 
        mandatory_opt=True, multi_opt=False
    )
    # -------------
    msg = """ 
    shows information about every machine/component of the platform
    """
    show.define_option("state", description=msg)
    # -------------
    msg = """ 
    displays a diagram that explains the structure of the platform
    """
    show.define_option("diagram", description=msg)
    # -------------
    msg = """ 
    shows information about the external dependencies of the program
    """
    show.define_option("dep", description=msg)
    # -------------
    msg = """ 
    shows important information about how the platform is built and 
    deployed, and the requirements that the container images need to 
    fulfill, in order to fit into the platform (in case an specific
    image is passed to the program)
    """
    show.define_option("info", description=msg)
    # -------------
    cli.add_command(show)
    _commands[cmd_name] = commands_rep.show
    
    # ++++++++++++++++++++++++++++
    cmd_name = "term"
    msg = """ 
    <void or container_names> opens the terminal of the containers 
    specified or all of them if no name is given
    """
    term = Command(
        cmd_name, description=msg, 
        extra_arg=True, multi=True
    )
    cli.add_command(term)
    _commands[cmd_name] = commands_rep.term
    
    # ++++++++++++++++++++++++++++
    cmd_name = "publish"
    msg = """ 
    <container_name> publish the image of the container specified
    """
    publish = Command(
        cmd_name, description=msg, 
        extra_arg=True, mandatory=True
    )
    publish.define_option(
        "--alias", description="allows to specify the alias of the image",
        extra_arg=True, mandatory=True
    )
    cli.add_command(publish)
    _commands[cmd_name] = commands_rep.publish


def _def_loadbalancer_cmds(cli:Cli):
    pass

def _def_client_cmds(cli:Cli):
    pass

def _def_database_cmds(cli:Cli):
    pass


    # -------------

def _config_cli() -> Cli:
    """Se definen todos los argumentos que podra recibir el programa 
    (se asocia cada comando principal con una funcion y se almacena 
    en commands) y se configura la command line interface (cli)

    Returns:
            Cli: Devuelve la cli configurada con los comandos del 
                programa
    """
    global _commands
    cli = Cli()
    # Arguments
    # ++++++++++++++++++++++++++++
    
    
    
    # -------------
    msg = """ 
    adds clients instead of servers
    """
    add.define_option("-cl", description=msg)
    # -------------
    
    
    
    # ++++++++++++++++++++++++++++
    cmd_name = "change"
    msg = """ 
    allows to change some features of the platform
    """
    change = Command(
        cmd_name, description=msg,
        mandatory_opt=True,  multi_opt=False
    )
    # -------------
    msg = """ 
    changes the balance algorithm of the load balancer
    """
    change.define_option(
        "balance", description=msg, 
        extra_arg=True, mandatory=True
    )
    # -------------
    cli.add_command(change)
    _commands[cmd_name] = commands_rep.change
    
    # ++++++++++++++++++++++++++++
    
    # -------------
    _commands[cmd_name] = commands_rep.app

    # ++++++++++++++++++++++++++++
    
    
# --------------------------------------------------------------------