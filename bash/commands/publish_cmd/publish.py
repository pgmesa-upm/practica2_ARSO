
# Imports para definicion del comando
import logging
from dependencies.cli.aux_classes import Command, Flag, Option
# Imports para la funcion asociada al comando

from dependencies.lxc.lxc_classes.container import Container
from ..reused_functions import get_cs
from program.platform.machines import servers
from program.platform.machines import (
    servers, load_balancer, client, data_base
)
import dependencies.lxc.lxc as lxc


def get_publish_cmd():
    cmd_name = "publish"
    msg = """ 
    <container_name> publish the image of the container specified
    """
    publish = Command(
        cmd_name, description=msg, 
        extra_arg=True, mandatory=True
    )
    # ++++++++++++++++++++++++++++
    alias = _def_alias_opt()
    publish.add_option(alias)
    
    return publish
 
# --------------------------------------------------------------------
# --------------------------------------------------------------------   
def _def_alias_opt():
    alias = Option(
        "--alias", description="allows to specify the alias of the image",
        extra_arg=True, mandatory=True
    )
    return alias

# --------------------------------------------------------------------
# --------------------------------------------------------------------
publish_logger = logging.getLogger(__name__)
def publish(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={}):
    c_list = get_cs(args, options)
    if c_list is None: return
    c:Container = c_list[0]
    im_dict = lxc.lxc_image_list()
    aliases = []
    for f in im_dict:
        aliases.append(im_dict[f]["ALIAS"])
    if not "--alias" in options:
        if c.tag == servers.TAG:
            name = "tomcat8_serv"
        elif c.tag == data_base.TAG:
            name = "mongo_db"
        elif c.tag == load_balancer.TAG:
            name = "haproxy_lb"
        elif c.tag == client.TAG:
            name = "lynx_client"
        j = 0
        while name in aliases:
            j += 1
            if j == 1:
                name = f"{name}{j}"
                continue
            name = f"{name[:-1]}{j}"
    else:
        name = options["--alias"][0]
    if name in aliases:
        err_msg = (f" El alias '{name}' ya existe en el repositorio " +
                    "local de lxc")
        publish_logger.error(err_msg)
        return
    try:
        msg = (f" Publicando imagen de '{c.tag}' '{c}' con alias " + 
               f"'{name}' (puede tardar)...")
        publish_logger.info(msg)
        c.publish(alias=name)
        publish_logger.info(" Imagen publicada con exito")
    except Exception as err:
        publish_logger.error(err)