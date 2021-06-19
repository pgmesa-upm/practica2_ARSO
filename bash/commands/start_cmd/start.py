
import logging

# Imports para la definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from ..reused_definitions import reused_opts, reused_flags
# Imports para la funcion asociada al comando
from program import apps_handler
from program import program
from ..reused_functions import  get_cs
from dependencies.utils.tools import concat_array
from program.controllers import bridges, containers
from program.platform.machines import servers
from ..servs_cmd.mark_cmd.mark import mark
from ..term_cmd.term import term


# --------------------------------------------------------------------
def get_start_cmd():
    cmd_name = "start"
    msg = """ 
    <void or container_names> runs the containers specified, if 
    void all containers are runned
    """
    start = Command(
        cmd_name, description=msg, 
        extra_arg=True, multi=True
    )
    # ++++++++++++++++++++++++++++
    skip = reused_opts["--skip"]
    start.add_option(skip)
    # ++++++++++++++++++++++++++++
    use = _def_use_opt()
    start.add_option(use)
    # Flags ---------------------- 
    start.add_flag(reused_flags["-m"])
    start.add_flag(reused_flags["-t"])
    
    return start

# --------------------------------------------------------------------
# --------------------------------------------------------------------
def _def_use_opt():
    msg = """ 
    <app_name> allows to specify the app that will be deployed
    in the servers (if any server among the containers specified is 
    being started)
    """
    use = Option(
        "--use", description=msg, 
        extra_arg=True, mandatory=True
    )
    return use

# --------------------------------------------------------------------
# --------------------------------------------------------------------
start_logger = logging.getLogger(__name__)        
def start(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={},
          **extras):
    """Arranca los contenedores que se enceuntren en target_cs

    Args:
        options (dict, optional): Opciones del comando arrancar
        flags (list, optional): Flags introducidos en el programa
    """
    # Arrancamos los contenedores validos
    tags = []
    if "tags" in extras: tags = extras["tags"]
    target_cs = get_cs(args, options, tags=tags)
    if target_cs is None: return
    msg = f" Arrancando contenedores '{concat_array(target_cs)}'..."
    start_logger.info(msg)
    succesful_cs = containers.start(*target_cs)
    program.list_lxc_containers(*succesful_cs)
    cs_s = concat_array(succesful_cs)
    msg = (f" Los contenedores '{cs_s}' han sido arrancados \n")
    start_logger.info(msg)
    # Si nos lo indican, abrimos las terminales de los contenedores 
    # arrancados
    if "-t" in flags and len(succesful_cs) > 0:
        c_names = list(map(lambda c: c.name, target_cs))
        term(args=c_names, flags=flags)
    warn = (" Los servicios de los servidores y/o balanceador puede " +
            "tardar unos cuantos segundos en estar disponibles\n")
    start_logger.warning(warn)
    
    # Cargamos la aplicacion si es necesario
    if len(succesful_cs) > 0:
        if "--use" in options:
            servs = filter(lambda c: c.tag == servers.TAG, succesful_cs)
            servs_names = list(map(str, servs))
            if len(servs_names) > 0:
                app = options["--use"][0]
                msg = f" Cargando la aplicacion '{app}' en servidores..."
                start_logger.info(msg) 
                apps_handler.use_app(app, *servs_names)
                start_logger.info(" Distribucion de la aplicacion finalizado\n")
        elif apps_handler.get_defaultapp() is not None:
            servs_without_app = []
            for c in succesful_cs:
                if c.tag == servers.TAG and c.app is None:
                    servs_without_app.append(c.name)
            if len(servs_without_app) > 0:       
                msg = " Cargando la aplicacion por defecto en servidores..."
                start_logger.info(msg) 
                apps_handler.use_app("default", *servs_without_app)
                start_logger.info(" Distribucion de la aplicacion finalizado\n")
        else:
            warn = (" No hay ninguna aplicacion asignada como default " +
                    "para desplegar en los servidores\n")
            start_logger.warning(warn)
        if "-m" in flags:
            mark()