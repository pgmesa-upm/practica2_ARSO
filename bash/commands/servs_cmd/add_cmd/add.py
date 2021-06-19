
import logging

# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from ...reused_definitions import reused_opts, reused_flags
# Imports para la funcion asociada al comando
from program.platform.machines import servers
from program.controllers import containers
from program import program
from program.platform import platform
from dependencies.register import register
from dependencies.utils.tools import concat_array
from ...reused_functions import get_servers_opts
from ...start_cmd.start import start


def get_add_cmd():
    msg = """
    <void or number> creates the number of servers specified.
    If void, one is created"""
    add = Command(
        "add", description=msg,
        extra_arg=True, default=1, choices=[1,2,3,4,5]
    )
    # ++++++++++++++++++++++++++++
    name = reused_opts["--name"]
    add.add_option(name)
    # ++++++++++++++++++++++++++++
    image = _def_image_opt()
    add.add_option(image)
    # ++++++++++++++++++++++++++++
    use = _def_use_opt()
    add.add_option(use)
    # Flags ----------------------
    add.add_flag(reused_flags["-l"])
    add.add_flag(reused_flags["-m"])
    add.add_flag(reused_flags["-t"])
    
    return add

# -------------------------------------------------------------------- 
# -------------------------------------------------------------------- 
def _def_image_opt():
    image = Option(
        "--image", description="allows to specify the image",
        extra_arg=True, mandatory=True, multi=True
    )
    return image

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
# -------------------------------------------------------------------- 
add_logger = logging.getLogger(__name__)
def add(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={}):
    if not platform.is_deployed():
        msg = (
            " La plataforma de servidores no ha sido desplegada, se " +
            "debe crear una nueva antes de añadir los servidores"
        )
        add_logger.error(msg)
        return
    num = args[0] 
    existent_cs = register.load(containers.ID)
    if existent_cs != None:
        ex_s = filter(lambda cs: cs.tag == servers.TAG, existent_cs)
        n = len(list(ex_s))
        if n + num > 5: 
            msg = (f" La plataforma no admite mas de 5 servidores. " +
                    f"Existen {n} actualmente, no se " +
                    f"pueden añadir {num} mas")
            add_logger.error(msg)
            return
    image, names = get_servers_opts(options, flags)
    servs = servers.create_servers(num, *names, image=image)
    program.list_lxc_containers(*servs) 
    cs_s = concat_array(servs)
    msg = (f" Contenedores '{cs_s}' inicializados\n")
    add_logger.info(msg)
    if len(servs) > 0:
        add_logger.info(" Estableciendo conexiones " +
                                "entre contenedores y bridges...")
        platform.update_conexions()
        add_logger.info(" Conexiones establecidas\n")
        if "-l" in flags:
            init_serv_names = list(map(str, servs))
            start(args=init_serv_names, options=options, flags=flags)