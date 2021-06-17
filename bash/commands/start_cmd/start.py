
import logging

# Imports para la definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from ..reused_definitions import reused_opts, reused_flags
# Imports para la funcion asociada al comando
from program import apps_handler
from program import program
from ..reused_functions import target_containers
from dependencies.utils.tools import concat_array
from program.controllers import bridges, containers
from program.platform.machines import servers
from ..repo_cmd.apps_cmd.apps import apps
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
    # Flags ---------------------- 
    start.add_flag(reused_flags["-m"])
    start.add_flag(reused_flags["-t"])
    
    return start

# --------------------------------------------------------------------
# --------------------------------------------------------------------
start_logger = logging.getLogger(__name__)
@target_containers(start_logger)           
def start(*target_cs, options={}, flags=[]):
    """Arranca los contenedores que se enceuntren en target_cs

    Args:
        options (dict, optional): Opciones del comando arrancar
        flags (list, optional): Flags introducidos en el programa
    """
    # Arrancamos los contenedores validos
    msg = f" Arrancando contenedores '{concat_array(target_cs)}'..."
    start_logger.info(msg)
    succesful_cs = containers.start(*target_cs)
    if not "-q" in flags:
        program.list_lxc_containers()
    cs_s = concat_array(succesful_cs)
    msg = (f" Los contenedores '{cs_s}' han sido arrancados \n")
    start_logger.info(msg)
    # Si nos lo indican, abrimos las terminales de los contenedores 
    # arrancados
    if "-t" in flags and len(succesful_cs) > 0:
        c_names = list(map(lambda c: c.name, target_cs))
        term(*c_names, flags=flags)
    warn = (" Los servicios de los servidores y/o balanceador puede " +
            "tardar unos cuantos segundos en estar disponibles\n")
    start_logger.warning(warn)
    # Cargamos la aplicacion
    if apps_handler.get_defaultapp() is not None:
        servs = []
        for c in succesful_cs:
            if c.tag == servers.TAG and c.app is None:
                servs.append(c.name)
        if len(servs) > 0:
            msg = " Cargando la aplicacion por defecto en servidores..."
            start_logger.info(msg) 
            apps_handler.use_app("default", *servs)
            start_logger.info(" Distribucion de la aplicacion finalizado\n")
    else:
        warn = (" No hay ninguna aplicacion asignada como default " +
                "para desplegar en los servidores\n")
        start_logger.warning(warn)
    if "-m" in flags:
        apps(options={"markservs":{"args":[], "options":{}, "flags":[]}})