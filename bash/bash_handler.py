
import bash.repository.commands as commands_rep
from dependencies.cli.cli import Cli, CmdLineError
from dependencies.cli.aux_classes import Command, Flag

# --------------------------- BASH HANDLER ---------------------------
# --------------------------------------------------------------------
# Define todos los comandos que va a tener el programa y ejecuta las
# ordenes que introduzca el usuario por terminal
# --------------------------------------------------------------------

# En este diccionario se asocia a cada comando una funcion a ejecutar
_commands = {}
# --------------------------------------------------------------------
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
       cmd_name = "deploy"
       msg = (
              "<void or integer between(1-5)> --> " + 
              "deploys a server platform\n           with the number " +
              "of servers especified (if void, 2 servers are created). It\n " + 
              "          also initializes a load balancer that acts as a bridge " +
              "between the servers.\n           Everything is " +
              "connected by 2 virtual bridges"
       )
       deploy = Command(cmd_name, description=msg, extra_arg=True, 
                                   choices=[1,2,3,4,5], default=2)
       msg = ("<server_names> allows to specify the name of the servers, " + 
              "\n                      by default 's_' is given to each server")
       deploy.add_option("--name", description=msg, extra_arg=True, 
                                          multi=True, mandatory=True)
       msg = ("<void or client_name> creates a client connected to the load balancer")
       deploy.add_option("--client", description=msg, extra_arg=True)
       msg = ("<alias or fingerprint> allows to specify the image of the " +
              "containers,\n                      by default ubuntu:18.04 is used")
       deploy.add_option(
              "--image", description=msg, extra_arg=True, mandatory=True
       )
       msg ="<alias or fingerprint> allows to specify the image of the servers"
       deploy.add_option(
              "--simage", description=msg, extra_arg=True, mandatory=True
       )
       msg = "<alias or fingerprint> allows to specify the image of the load balancer"
       deploy.add_option(
              "--lbimage", description=msg, extra_arg=True, mandatory=True
       )
       msg = "<alias or fingerprint> allows to specify the image of the client"
       deploy.add_option(
              "--climage", description=msg, extra_arg=True, mandatory=True
       )
       msg = ("allows to specify the balance algorithm of the load balancer," + 
              "\n                      by default it uses 'roundrobin'")
       deploy.add_option(
              "--balance", description=msg, extra_arg=True, mandatory=True
       )
       cli.add_command(deploy)
       _commands[cmd_name] = commands_rep.deploy
       
       cmd_name = "start"
       msg = ("<void or container_names> runs the containers specified, " +
              "if void\n           all containers are runned")
       start = Command(cmd_name, description=msg, extra_arg=True, multi=True)
       cli.add_command(start)
       _commands[cmd_name] = commands_rep.start
       
       cmd_name = "stop"
       msg = ("<void or container_names> stops the containers currently " +
              "running,\n           if void all containers are stopped")
       stop = Command(cmd_name, description=msg, extra_arg=True, multi=True)
       cli.add_command(stop)
       _commands[cmd_name] = commands_rep.stop
       
       cmd_name = "destroy"
       msg = ("deletes every component of the platform created")
       destroy = Command(cmd_name, description=msg)
       cli.add_command(destroy)
       _commands[cmd_name] = commands_rep.destroy
       
       # Other functionalities
       cmd_name = "pause"
       msg = ("<void or container_names> pauses the containers currently " +
              "running,\n           if void all containers are stopped")
       pause = Command(cmd_name, description=msg, extra_arg=True, multi=True)
       cli.add_command(pause)
       _commands[cmd_name] = commands_rep.pause

       cmd_name = "add"
       msg = ("<integer between(1-5)> adds the number of servers specified " +
              " (the\n           program can't surpass 5 servers)")
       add = Command(cmd_name, description=msg, extra_arg=True, 
                                   choices=[1,2,3,4,5], mandatory=True)
       msg = ("<server_names> allows to specify the name of the servers, " + 
              "\n                      by default 's_' is given to each server")
       add.add_option("--name", description=msg, extra_arg=True, 
                                          multi=True, mandatory=True)
       msg = ("adds clients instead of servers")
       add.add_option("-cl", description=msg)
       msg ="<alias or fingerprint> allows to specify the image"
       add.add_option("--image", description=msg, extra_arg=True, mandatory=True)
       cli.add_command(add)
       _commands[cmd_name] = commands_rep.add
       
       cmd_name = "remove"
       msg = ("<void or container_names> deletes the containers specified, if void " +
              "\n           all containers are deleted (some may not be removable)")
       remove = Command(cmd_name, description=msg, extra_arg=True,  multi=True)
       cli.add_command(remove)
       _commands[cmd_name] = commands_rep.remove
       
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
       msg = "'warning mode', only shows warning and error msgs during execution"
       verbosity = Flag("-w", notCompatibleWithFlags=["-d"], description=msg)
       cli.add_flag(verbosity)
       msg = "option for debugging"
       debugging = Flag("-d", notCompatibleWithFlags=["-w"], description=msg)
       cli.add_flag(debugging)
       msg = ("'quiet mode', doesn't show any msg " + 
              "during execution (only when an error occurs)")
       quiet = Flag("-q", notCompatibleWithFlags=["-w","-d"], description=msg)
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
