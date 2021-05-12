
import logging

import bash.repository.commands as commands_rep
from dependencies.cli.cli import Cli, CmdLineError
from dependencies.cli.aux_classes import Command, Flag
from dependencies.utils.decorators import timer

# --------------------------- BASH HANDLER ---------------------------
# --------------------------------------------------------------------
# Define todos los comandos que va a tener el programa y ejecuta las
# ordenes que introduzca el usuario por terminal
# --------------------------------------------------------------------

# En este diccionario se asocia a cada comando una funcion a ejecutar
_commands = {}
# --------------------------------------------------------------------
@timer
def execute(args:dict):
    """Ejecuta la funcion correspondiente al comando introducido por 
    el usuario

    Args:
        args (dict): Linea de comandos introducida por el usuario 
            ya validada, es decir, debe ser correcta
    """
    for cmd_name, cmd in _commands.items():
        if cmd_name in args["cmd"]:
            principal = args.pop("cmd").pop(cmd_name)
            secundary = args
            cmd(*principal, **secundary)
            break
        
# --------------------------------------------------------------------
def config_cli() -> Cli:
    """Se definen todos los argumentos que podra recibir el programa 
    (se asocia cada comando principal con una funcion y se almacena 
    en commands) y se configura la command line interface (cli)

    Returns:
       Cli: Devuelve la cli configurada con los comandos del programa
    """
    global _commands
    cli = Cli()
    # Arguments
    cmd_name = "crear"
    msg = (
        "<void or integer between(1-5)> --> " + 
        "deploys a server platform\n           with the number " +
        "of servers especified (if void, 2 servers are created). It\n " + 
        "          also initializes a load balancer that acts as a bridge " +
        "between the servers.\n           Everything is " +
        "connected by 2 virtual bridges"
    )
    crear = Command(cmd_name, description=msg, extra_arg=True, 
                                choices=[1,2,3,4,5], default=2)
    msg = ("<server_names> allows to specify the name of the servers, " + 
           "\n                      by default 's_' is given to each server")
    crear.add_option("--name", description=msg, extra_arg=True, 
                                        multi=True, mandatory=True)
    msg = ("<alias or fingerprint> allows to specify the image of the " +
           "containers,\n                      by default ubuntu:18.04 is used")
    crear.add_option("--image", description=msg, extra_arg=True, mandatory=True)
    msg ="<alias or fingerprint> allows to specify the image of the servers"
    crear.add_option("--simage", description=msg, extra_arg=True, mandatory=True)
    msg = "<alias or fingerprint> allows to specify the image of the load balancer"
    crear.add_option("--lbimage", description=msg, extra_arg=True, mandatory=True)
    msg = "<alias or fingerprint> allows to specify the image of the client"
    crear.add_option("--climage", description=msg, extra_arg=True, mandatory=True)
    cli.add_command(crear)
    _commands[cmd_name] = commands_rep.crear
    
    cmd_name = "arrancar"
    msg = ("<void or container_names> runs the containers specified, " +
           "if void\n           all containers are runned")
    arrancar = Command(cmd_name, description=msg, extra_arg=True, multi=True)
    cli.add_command(arrancar)
    _commands[cmd_name] = commands_rep.arrancar
    
    cmd_name = "parar"
    msg = ("<void or container_names> stops the containers currently " +
          "running,\n           if void all containers are stopped")
    parar = Command(cmd_name, description=msg, extra_arg=True, multi=True)
    cli.add_command(parar)
    _commands[cmd_name] = commands_rep.parar
    
    cmd_name = "destruir"
    msg = ("deletes every component of the platform created")
    destruir = Command(cmd_name, description=msg)
    cli.add_command(destruir)
    _commands[cmd_name] = commands_rep.destruir
    
    # Other functionalities
    cmd_name = "pausar"
    msg = ("<void or container_names> pauses the containers currently " +
          "running,\n           if void all containers are stopped")
    pausar = Command(cmd_name, description=msg, extra_arg=True, multi=True)
    cli.add_command(pausar)
    _commands[cmd_name] = commands_rep.pausar

    cmd_name = "añadir"
    msg = ("<integer between(1-5)> adds the number of servers specified " +
           " (the\n           program can't surpass 5 servers)")
    añadir = Command(cmd_name, description=msg, extra_arg=True, 
                                choices=[1,2,3,4,5], mandatory=True)
    msg = ("<server_names> allows to specify the name of the servers, " + 
           "\n                      by default 's_' is given to each server")
    añadir.add_option("--name", description=msg, extra_arg=True, 
                                        multi=True, mandatory=True)
    msg ="<alias or fingerprint> allows to specify the image of the servers"
    añadir.add_option("--simage", description=msg, extra_arg=True, mandatory=True)
    cli.add_command(añadir)
    _commands[cmd_name] = commands_rep.añadir
    
    cmd_name = "eliminar"
    msg = ("<void or server_names> deletes the servers specified, if void " +
          "\n           all servers are deleted")
    eliminar = Command(cmd_name, description=msg, extra_arg=True,  multi=True)
    cli.add_command(eliminar)
    _commands[cmd_name] = commands_rep.eliminar
    
    cmd_name = "show"
    msg = "shows information about the program"
    show = Command(cmd_name, description=msg, mandatory_opt=True, multi_opt=False)
    msg = "shows information about every machine/component of the platform"
    show.add_option("state", description=msg)
    msg ="displays a diagram that explains the structure of the platform"
    show.add_option("diagram", description=msg)
    msg ="shows information about the external dependencies of the program"
    show.add_option("dep", description=msg)
    cli.add_command(show)
    _commands[cmd_name] = commands_rep.show
    
    cmd_name = "term"
    msg = ("<void or container_names> opens the terminal of the containers " + 
           "\n           specified or all of them if no name is given")
    term = Command(cmd_name, description=msg, extra_arg=True, multi=True)
    cli.add_command(term)
    _commands[cmd_name] = commands_rep.term
    
    #Flags/Options
    msg = "shows information about every process that is being executed"
    verbosity = Flag("-v", notCompatibleWithFlags=["-d"], description=msg)
    cli.add_flag(verbosity)
    msg = "option for debugging"
    debugging = Flag("-d", notCompatibleWithFlags=["-v"], description=msg)
    cli.add_flag(debugging)
    msg = ("'quiet mode', doesn't show any msg " + 
            "during execution (only when an error occurs)")
    quiet = Flag("-q", notCompatibleWithFlags=["-v","-d"], description=msg)
    cli.add_flag(quiet)
    msg = "executes the action without asking confirmation"
    force = Flag("-f", description=msg)
    cli.add_flag(force)
    msg = "opens the terminal window of the containers that are being runned"
    terminal = Flag("-t", description=msg)
    cli.add_flag(terminal)
    msg = "launches the container"
    launch = Flag("-l", description=msg)
    cli.add_flag(launch)
    return cli
# --------------------------------------------------------------------
