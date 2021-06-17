
import logging

# Imports para la definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from ..reused_definitions import reused_opts, reused_flags
# Imports para la funcion asociada al comando
from program import program
from program.platform import platform
from ..reused_functions import get_cs
from dependencies.utils.tools import concat_array, remove_many
from program.controllers import bridges, containers
from program.platform.machines import (
    servers, load_balancer, net_devices, client, data_base
)

def get_delete_cmd():
    cmd_name = "delete"
    msg = """ 
    <void or container_names> deletes the containers 
    specified, if void all containers are deleted (only servers
    and clients)
    """
    delete = Command(
        cmd_name, description=msg, 
        extra_arg=True,  multi=True
    )
    # ++++++++++++++++++++++++++++
    skip = reused_opts["--skip"]
    delete.add_option(skip)
    # Flags ---------------------- 
    delete.add_flag(reused_flags["-y"])
    
    return delete

# --------------------------------------------------------------------
# --------------------------------------------------------------------
delete_logger = logging.getLogger(__name__)
def delete(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={},
           **extras): 
    """Elimina los contenedores que se enceuntren en target_cs.
    Por defecto, esta funcion solo elimina los contenedores que 
    sean servidores o clientes

    Args:
        options (dict, optional): Opciones del comando eliminar
        flags (list, optional): Flags introducidos en el programa
        skip_tags (list, optional): Variable que permite que destruir
            se comunique con esta funcion. Por defecto esta funcion 
            no elimina contenedores que sean clientes o balanceadores
    """
    # Miramos que contenedores son validos para eliminar
    tags = [servers.TAG, client.TAG]
    if "tags" in extras: tags = extras["tags"]
    target_cs = get_cs(args, options, tags=tags)
    if target_cs is None: return
    if not "-y" in flags:
        print("Se eliminaran los contenedores:" +
                    f" '{concat_array(target_cs)}'")
        answer = str(input("¿Estas seguro?(y/n): "))
        if answer.lower() != "y":
            return
    # Eliminamos los existentes que nos hayan indicado
    msg = f" Eliminando contenedores '{concat_array(target_cs)}'..."
    delete_logger.info(msg)
    succesful_cs = containers.delete(*target_cs)
    # Actualizamos la plataforma
    platform.update_conexions()
    program.list_lxc_containers()
    cs_s = concat_array(succesful_cs)
    msg = (f" Los contenedores '{cs_s}' han sido eliminados \n")
    delete_logger.info(msg)