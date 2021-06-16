
import logging

# Imports para la definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from ..reused_definitions import reused_opts, reused_flags
# Imports para la funcion asociada al comando
from program import program
from program.platform import platform
from ..reused_functions import target_containers
from dependencies.utils.tools import concat_array
from program.controllers import bridges, containers
from program.platform.machines import (
    servers, load_balancer, net_devices, client, data_base
)

def get_delete_cmd():
    cmd_name = "delete"
    msg = """ 
    <void or container_names> deletes the containers 
    specified, if void all containers are deleted (some 
    may not be removable)
    """
    delete = Command(
        cmd_name, description=msg, 
        extra_arg=True,  multi=True
    )
    return delete

# --------------------------------------------------------------------
delete_logger = logging.getLogger(__name__)
@target_containers(delete_logger) 
def delete(*target_cs, options={}, flags=[],
            skip_tags=[load_balancer.TAG, data_base.TAG]): 
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
    if len(skip_tags) > 0:
        valid_cs = []
        for c in target_cs:
            if c.tag in skip_tags:
                msg = (f" El contenedor '{c}' no se puede eliminar " + 
                        "(solo servidores o clientes)")
                delete_logger.error(msg)  
                continue
            valid_cs.append(c)
        if len(valid_cs) == 0: return
        target_cs = valid_cs
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
    if not "-q" in flags:
        program.list_lxc_containers()
    cs_s = concat_array(succesful_cs)
    msg = (f" Los contenedores '{cs_s}' han sido eliminados \n")
    delete_logger.info(msg)