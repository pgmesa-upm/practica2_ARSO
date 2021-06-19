
from bash.commands.loadbal_cmd.set_cmd.port_cmd.port import port
import logging
import concurrent.futures as conc

# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from ..reused_definitions import reused_opts, reused_flags
# Imports para la funcion asociada al comando
from program.controllers import bridges, containers
from program import program
from program.platform import platform
from dependencies.utils.tools import concat_array
from ..reused_functions import (
    get_db_opts, get_cl_opts, get_lb_opts, get_servers_opts
)
from program.platform.machines import (
    servers, load_balancer, net_devices, client, data_base
)
from ..start_cmd.start import start


# --------------------------------------------------------------------
def get_deploy_cmd():
    cmd_name = "deploy"
    msg = """
    <void or integer between(1-5)> --> deploys a server platform with
    the number of servers especified (if void, 2 servers are created).
    It also initializes a load balancer that acts as a bridge between 
    the servers and a data base for storing data. Everything is 
    connected by 2 virtual bridges
    """
    deploy = Command(
        cmd_name, description=msg, 
        extra_arg=True, choices=[1,2,3,4,5], default=2
    )
    # ++++++++++++++++++++++++++++
    image = _def_image_opt()
    deploy.add_option(image)
    # ++++++++++++++++++++++++++++
    simage = _def_simage_opt()
    deploy.add_option(simage)
    # ++++++++++++++++++++++++++++
    name = _def_name_opt()
    deploy.add_option(name)
    # ++++++++++++++++++++++++++++
    use = _def_use_opt()
    deploy.add_option(use)
    # ++++++++++++++++++++++++++++
    lbimage = _def_lbimage_opt()
    deploy.add_option(lbimage)
    # ++++++++++++++++++++++++++++
    balance = _def_balance_opt()
    deploy.add_option(balance)
    # ++++++++++++++++++++++++++++
    port = _def_port_opt()
    deploy.add_option(port)
    # ++++++++++++++++++++++++++++
    dbimage = _def_dbimage_opt()
    deploy.add_option(dbimage)
    # ++++++++++++++++++++++++++++
    client = _def_client_opt()
    deploy.add_option(client)
    # ++++++++++++++++++++++++++++
    climage = _def_climage_opt()
    deploy.add_option(climage)
    
    # Flags ---------------------- 
    deploy.add_flag(reused_flags["-l"])
    deploy.add_flag(reused_flags["-t"])
    deploy.add_flag(reused_flags["-m"])
    
    return deploy

# --------------------------------------------------------------------
# -------------------------------------------------------------------- 
def _def_image_opt():
    msg = """ 
    <alias or fingerprint> allows to specify the image of the
    containers, by default ubuntu:18.04 is used
    """
    image = Option(
        "--image", description=msg, 
        extra_arg=True, mandatory=True
    )
    return image

# -------------------------------------------------------------------- 
def _def_simage_opt():
    msg = """ 
    <alias or fingerprint> allows to specify the image of the 
    servers
    """
    simage = Option(
        "--simage", description=msg, 
        extra_arg=True, mandatory=True
    )
    return simage

def _def_name_opt():
    msg = """
    <server_names> allows to specify the names of the servers"""
    name = Option(
        "--name", description=msg,
        extra_arg=True, mandatory=True, multi=True
    )
    return name

def _def_use_opt():
    msg = """ 
    <app_name> allows to specify the app that will be deployed
    in the servers (if they are being runned)
    """
    use = Option(
        "--use", description=msg, 
        extra_arg=True, mandatory=True
    )
    return use

# -------------------------------------------------------------------- 
def _def_lbimage_opt():
    msg = """ 
    <alias or fingerprint> allows to specify the image of the 
    load balancer
    """
    lbimgae = Option(
        "--lbimage", description=msg, 
        extra_arg=True, mandatory=True
    )
    return lbimgae

def _def_balance_opt():
    msg = """ 
    <algorithm_name> allows to specify the balance algorithm of the
    load balancer (roundrobin, leastconn, source, ...). By default 
    'roundrobin' is used
    """
    balance = Option(
        "--balance", description=msg, 
        extra_arg=True, mandatory=True
    )
    return balance

def _def_port_opt():
    msg = """<port_number> changes the port where the load balancer
    is listening (default -> 80)"""
    port = Option(
        "--port", description=msg, 
        extra_arg=True, mandatory=True
    )
    return port

# -------------------------------------------------------------------- 
def _def_dbimage_opt():
    msg = """ 
    <alias or fingerprint> allows to specify the image of the 
    data base
    """
    dbimage = Option(
        "--dbimage", description=msg, 
        extra_arg=True, mandatory=True
    )
    return dbimage

# --------------------------------------------------------------------
def _def_client_opt():
    msg = """ 
    <void or client_name> creates a client connected to the load 
    balancer
    """
    client = Option("--client", description=msg, extra_arg=True)
    return client
 
def _def_climage_opt():
    msg = """ 
    <alias or fingerprint> allows to specify the image of the 
    client
    """
    climage = Option(
        "--climage", description=msg, 
        extra_arg=True, mandatory=True
    )
    return climage

# -------------------------------------------------------------------- 
# -------------------------------------------------------------------- 
deploy_logger = logging.getLogger(__name__)
def deploy(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={}):
    """Crea la plataforma del sistema-servidor, desplegando los 
    bridges y contenedores y conectandolos entre ellos (de la forma
    que se hayan definido estas conexiones en la carpeta program)

    Args:
        numServs (int): Numero de servidores a crear
        options (dict, optional): Opciones del comando crear
        flags (list, optional): Flags introducidos en el programa
    """
    if platform.is_deployed():
        msg = (" La plataforma de servidores ya ha sido desplegada, " 
              + "se debe destruir la anterior para crear otra nueva")
        deploy_logger.error(msg)
        return   
    deploy_logger.info(" Desplegando la plataforma de servidores...\n")
    # Creando bridges
    bgs = net_devices.get_bridges(numBridges=2)
    bgs_s = concat_array(bgs)
    deploy_logger.debug(f" Nombre de bridges (objetos) --> '{bgs_s}'")
    deploy_logger.info(" Creando bridges...")
    successful_bgs = bridges.init(*bgs)
    program.list_lxc_bridges(*successful_bgs)
    bgs_s = concat_array(successful_bgs)
    deploy_logger.info(f" Bridges '{bgs_s}' creados\n")
    # Creando contenedores
    num_servs = args[0]
    dbimage = get_db_opts(options, flags)
    lbimage, algorithm, port = get_lb_opts(options, flags)
    if "--client" in options:
        climage, clname = get_cl_opts(options, flags)
    simage, names = get_servers_opts(options, flags)
    # Configurando e Iniciando contenedores
    successful_cs = []
    if "-s" in flags:
        db = data_base.create_database(image=dbimage)
        if db is not None: successful_cs.append(db)
        lb = load_balancer.create_lb(
            image=lbimage, balance=algorithm, port=port
        )
        if lb is not None: successful_cs.append(lb)
        if "--client" in options:
            cl = client.create_client(name=clname, image=climage)
            if cl is not None: successful_cs.append(cl)
        servs = servers.create_servers(num_servs, *names, image=simage)
        successful_cs += servs
    else:
        # Utilizamos concurrencia de hilos
        with conc.ThreadPoolExecutor() as executor:
            threads = []
            db_thread = executor.submit(
                data_base.create_database, image=dbimage
            )
            threads.append(db_thread)
            lb_thread = executor.submit(
                load_balancer.create_lb, 
                image=lbimage, balance=algorithm, port=port
            )
            threads.append(lb_thread)
            if "--client" in options:
                cl_thread = executor.submit(
                    client.create_client, name=clname, image=climage
                )
                threads.append(cl_thread)
            servs_thread = executor.submit(
                servers.create_servers, num_servs, *names, image=simage
            )
            threads.append(servs_thread)
            for thr in threads:
                container = thr.result()
                if type(container) is list:
                    successful_cs += container
                elif container != None:
                    successful_cs.append(container)
    # Mostramos la informacion y comprobamos flag de arranque
    program.list_lxc_containers(*successful_cs) 
    cs_s = concat_array(successful_cs)
    msg = (f" Contenedores '{cs_s}' inicializados\n")
    deploy_logger.info(msg)
    if len(successful_cs) > 0:
        deploy_logger.info(" Estableciendo conexiones " +
                                "entre contenedores y bridges...")
        platform.update_conexions()
        deploy_logger.info(" Conexiones establecidas\n")
        if "-l" in flags:
            c_names = list(map(lambda c: c.name, successful_cs))
            start(args=c_names, options=options, flags=flags)
    deploy_logger.info(" Plataforma de servidores desplegada")