
import logging

# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from ...reused_definitions import reused_opts, reused_flags
# Imports para la funcion asociada al comando
from program.platform.machines import load_balancer
from program.platform import platform
from program import program
from program.platform import platform
from ...start_cmd.start import start
from ...reused_functions import get_lb_opts

def get_add_cmd():
    msg = """creates a container with haproxy installed 
    in order to act as a load balancer"""
    add = Command("add", description=msg)
    # ++++++++++++++++++++++++++++
    # name = _def_name_opt()
    # add.add_option(name)
    # ++++++++++++++++++++++++++++
    image = _def_image_opt()
    add.add_option(image)
    # ++++++++++++++++++++++++++++
    balance = _def_balance_opt()
    add.add_option(balance)
    # ++++++++++++++++++++++++++++
    port = _def_port_opt()
    add.add_option(port)
    # Flags ----------------------
    add.add_flag(reused_flags["-l"])
    add.add_flag(reused_flags["-t"])
    
    return add

def _def_image_opt():
    image = Option(
        "--image", description="allows to specify the image",
        extra_arg=True, mandatory=True
    )
    return image

def _def_name_opt():
    name = Option(
        "--name", description="allows to specify the name",
        extra_arg=True, mandatory=True
    )
    return name

def _def_balance_opt():
    msg = """allows to specify the balance algorithm"""
    balance = Option(
        "--balance", description=msg,
        extra_arg=True, mandatory=True
    )
    return balance

def _def_port_opt():
    msg = """allows to specify the port of the container where 
        haproxy is going to be listening"""
    port = Option(
        "--port", description=msg,
        extra_arg=True, mandatory=True
    )
    return port

# --------------------------------------------------------------------
# --------------------------------------------------------------------
add_logger = logging.getLogger(__name__)
def add(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={}):
    if not platform.is_deployed():
        msg = " La plataforma no ha sido desplegada"
        add_logger.error(msg)
        return
    lb = load_balancer.get_lb()
    if lb is not None: 
        msg = (f" Ya existe un balanceador en la plataforma '{lb}', " + 
                "no se permiten mas")
        add_logger.error(msg)
        return
    image, balance, port = get_lb_opts(options, flags)
    lb = load_balancer.create_lb(image=image, balance=balance, port=port)
    if lb is not None:
        program.list_lxc_containers(lb) 
        msg = (f" Balanceador '{lb}' inicializado\n")
        add_logger.info(msg)
        add_logger.info(" Estableciendo conexiones ...")
        platform.update_conexions()
        add_logger.info(" Conexiones establecidas\n")
        if "-l" in flags:
            start(args=[lb.name], options=options, flags=flags)
    else:
        msg = (f" Fallo al crear el balanceador")
        add_logger.error(msg)