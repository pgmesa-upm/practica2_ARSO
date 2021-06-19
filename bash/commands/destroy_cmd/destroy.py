
import logging

# Imports para la definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from ..reused_definitions import reused_opts, reused_flags
# Imports para la funcion asociada al comando
from program import program
from program.platform import platform
from dependencies.utils.tools import concat_array
from program.controllers import bridges, containers
from dependencies.register import register
from ..delete_cmd.delete import delete


# --------------------------------------------------------------------
def get_destroy_cmd():
    cmd_name = "destroy"
    msg = """ 
    deletes every component of the platform created
    """
    destroy = Command(cmd_name, description=msg)
    # Flags ---------------------- 
    destroy.add_flag(reused_flags["-y"])
    
    return destroy

# --------------------------------------------------------------------
# --------------------------------------------------------------------
destroy_logger = logging.getLogger(__name__)
def destroy(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={}):
    """Destruye la platafrma del sistema-servidor eliminando todos
    sus componenetes (bridges, contenedores y las conexiones entre
    ellos). Reutiliza el codigo de la funcion eliminar para eliminar
    los contenedores.

    Args:
        options (dict, optional): Opciones del comando destruir
        flags (list, optional): Flags introducidos en el programa
    """
    if not platform.is_deployed():
        msg = (" La plataforma de servidores no ha sido desplegada, " 
                 + "se debe crear una nueva antes de poder destruir")
        destroy_logger.error(msg)
        return
    if not "-y" in flags:
        msg = ("Se borrara por completo la infraestructura " + 
                "creada, contenedores, bridges y sus conexiones " + 
                    "aun podiendo estar arrancadas")
        print(msg)
        answer = str(input("¿Estas seguro?(y/n): "))
        if answer.lower() != "y":
            return
    destroy_logger.info(" Destruyendo plataforma...\n")
    # Eliminamos contenedores
    cs = register.load(containers.ID)
    if cs == None:
        destroy_logger.warning(" No existen contenedores en el programa\n")
    else:
        c_names = list(map(lambda c: c.name, cs))
        flags.append("-y") # Añadimos el flag -y
        delete(args=c_names, flags=flags)
    # Eliminamos bridges
    bgs = register.load(bridges.ID)
    if bgs == None: 
        destroy_logger.warning(" No existen bridges en el programa")
    else:
        msg = f" Eliminando bridges '{concat_array(bgs)}'..."
        destroy_logger.info(msg)
        successful_bgs = bridges.delete(*bgs)
        bgs_s = concat_array(successful_bgs)
        msg = (f" Bridges '{bgs_s}' eliminados\n")
        destroy_logger.info(msg)  
        
        failed_bgs = list(filter(lambda b: b not in successful_bgs, bgs))
        if len(failed_bgs) > 0:
            program.list_lxc_bridges(*failed_bgs)
            bgs_f = concat_array(failed_bgs)
            msg = (f" No se han podido eliminar los bridge '{bgs_f}'\n")
            destroy_logger.error(msg)
    # Vemos si se ha eliminado todo  
    cs = register.load(containers.ID)
    bgs = register.load(bridges.ID) 
    if cs == None and bgs == None:
        register.remove("updates")
        destroy_logger.info(" Plataforma destruida")
    else:
        msg = (" Plataforma destruida parcialmente " +
                        "(se han encontrado dificultades)") 
        destroy_logger.error(msg)