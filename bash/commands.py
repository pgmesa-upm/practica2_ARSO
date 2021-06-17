
import logging
import concurrent.futures as conc

from ..commands.reused_functions import (
    target_containers, get_db_opts, get_cl_opts,
    get_lb_opts, get_servers_opts
)
from program.controllers import bridges, containers
from program.platform.machines import (
    servers, load_balancer, net_devices, client, data_base
)
from program import apps_handler
from program import program
from dependencies.register import register
from dependencies.utils.tools import concat_array
import dependencies.lxc.lxc as lxc
from dependencies.lxc.lxc_classes.container import Container
from program.platform import platform

# --------------------- REPOSITORIO DE COMANDOS ----------------------
# --------------------------------------------------------------------
# Aqui se definen todas las funciones asociadas a los comandos que 
# tiene el programa. Estas funciones se pueden comunicar entre si 
# mediante variables opcionales adicionales para reutilizar el codigo
# --------------------------------------------------------------------

cmd_logger = logging.getLogger(__name__)

    # --------------------------------------------------------------------
def add(num:int, options={}, flags=[], extra_cs=[]):
    """Añade el numero de contenedores especificados a la plataforma
    de servidores. Por defecto solo añade contenedores que sean del
    tipo servidor, pero en extra_cs se pueden especificar contenedores 
    de cualquier tipo que tambien se quiran añadir

    Args:
        numServs (int): Numero de servidores a añadir
        options (dict, optional): Opciones del comando añadir
        flags (list, optional): Flags introducidos en el programa
        extra_cs (list, optional): Variable utilizada para que 'crear' se
            pueda comunicar con esta funcion y tambien cree los 
            clientes y el balanceador, ademas de los servidores
    """
    if not platform.is_deployed():
        msg = (
            " La plataforma de servidores no ha sido desplegada, se " +
            "debe crear una nueva antes de añadir los servidores"
        )
        cmd_logger.error(msg)
        return
    
    existent_cs = register.load(containers.ID)
    if "-cl" in options:
        climage, name = get_cl_opts(options, flags)
        client.create_client(name=name, image=climage)
        return
    elif num > 0:
        if existent_cs != None:
            ex_s = filter(lambda cs: cs.tag == servers.TAG, existent_cs)
            n = len(list(ex_s))
            if n + num > 5: 
                msg = (f" La plataforma no admite mas de 5 servidores. " +
                        f"Existen {n} actualmente, no se " +
                        f"pueden añadir {num} mas")
                cmd_logger.error(msg)
                return
        simage, names = get_servers_opts(options, flags)
        servs = servers.create_servers(num, *names, image=simage)
        
    successful_cs = extra_cs + servs
    if not "-q" in flags:
        program.list_lxc_containers() 
    cs_s = concat_array(successful_cs)
    msg = (f" Contenedores '{cs_s}' inicializados\n")
    cmd_logger.info(msg)
    if len(successful_cs) > 0:
        cmd_logger.info(" Estableciendo conexiones " +
                                "entre contenedores y bridges...")
        platform.update_conexions()
        cmd_logger.info(" Conexiones establecidas\n")
        if "-l" in flags:
            c_names = list(map(lambda c: c.name, successful_cs))
            start(*c_names, options=options, flags=flags)
                 
# --------------------------------------------------------------------



            
# --------------------------------------------------------------------   
def change(options={}, flags={}):
    if "balance" in options:
        algorithm = options["balance"]["args"][0]
        load_balancer.change_algorithm(algorithm)

        
# -------------------------------------------------------------------- 
def show(options={}, flags={}):
    """Muestra informacion sobre el programa

    Args:
        choice (str): Indica que informacion se quiere mostrar
        options (dict, optional): Opciones del comando show
        flags (list, optional): Flags introducidos en el programa
    """
    if "diagram" in options:
        program.show_platform_diagram()
    elif "state" in options:
        platform.print_state()
    elif "dep" in options:
        program.show_dependencies()
    elif "info" in options:
        platform.print_info()
        
# --------------------------------------------------------------------

        