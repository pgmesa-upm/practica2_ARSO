
import re
import logging
import platform as plt
import subprocess
from functools import reduce

from dependencies.utils.lxc_functions import (
    lxc_list, 
    lxc_network_list,
    lxclist_as_dict
)
import program.controllers.bridges as bridges
import program.controllers.containers as containers
import dependencies.register.register as register
from .platform import platform

# --------------------- FUNCIONES DE PROGRAMA ------------------------
# --------------------------------------------------------------------
# Este fichero se encarga de proporcionar funciones especificas del
# programa. Realiza comprobaciones de entorno (revisa dependencias, si 
# ha habido cambios en los elementos de la plataforma desde fuera del
# programa, etc)
# --------------------------------------------------------------------

class ProgramError(Exception):
    pass
# --------------------------------------------------------------------
program_logger = logging.getLogger(__name__)
_dependencies = {}
# --------------------------------------------------------------------
def show_platform_diagram():
    """Muestra un diagrama que explica la finalidad del programa"""
    try:
        path = "program/resources/images/diagram.png"
        subprocess.Popen(
            ["display", path],
            stdout=subprocess.PIPE
        ) 
    except Exception as err:
        if "display" in str(err):
            program_logger.error("Se necesita instalar 'imagemagick'")
        else:
            program_logger.error(err)
        
def show_dependencies():
    """Muestra la estructura de ficheros utilizada para este proyecto
    y sus relaciones. Tambien muestra las dependencias externas a las
    que esta ligado"""
    pass

# --------------------------------------------------------------------
def list_lxc_containers():
    ips = 0
    cs = register.load(containers.ID)
    if cs is not None:
        program_logger.info(" Cargando resultados...")
        running = list(filter(lambda c: c.state == "RUNNING", cs))
        frozen = list(filter(lambda c: c.state == "FROZEN", cs))
        total = running+frozen
        ips = reduce(lambda acum, c: acum+len(c.networks), total, 0)
    try:
        lxc_list(ips_to_wait=ips)
    except Exception as err:
        program_logger.error(err)

def list_lxc_bridges():
    lxc_network_list()
    
# --------------------------------------------------------------------   
def check_enviroment():
    """Revisa que todas las dependencias externas que necesita el 
    programa se encuentran disponibles en el PC y en caso contrario 
    lanza un error si la dependencia es obligatoria o un warning si
    es opcional. 

    Raises:
        ProgramError: Si el SO que se esta usando no es Linux
        ProgramError: Si lxd no esta instalado
    """
    system = plt.system()
    program_logger.debug(f" {system} OS detected")
    if system != "Linux":
        err = (" Este programa solo funciona sobre " + 
                        f"Linux -> {system} detectado")
        raise ProgramError(err)
    try:
        subprocess.run(
            ["lxd", "--version"],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        subprocess.run(["lxd", "init", "--auto"])
    except:
        err = (" 'lxd' no esta instalado en este ordenador y es " +
               "necesario para la ejecucion del programa.\nIntroduce " +
               "'sudo apt install lxd' en la linea de comandos para "
               "instalarlo")
        raise ProgramError(err)
    try:
        subprocess.run(
            ["xterm", "--version"],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
    except:
        warn = (" 'xterm' no esta instalado en este ordenador y " +
              "algunas funcionalidades pueden requerir este modulo. " + 
              "Introduce 'sudo apt install xterm' en la linea de " + 
              "comandos para instalarlo")
        program_logger.warning(warn)
    try:
        subprocess.run(
            ["convert", "--version"],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
    except:
        warn = (" 'imagemagick' no esta instalado en este ordenador y " +
              "algunas funcionalidades pueden requerir este modulo. " + 
              "Introduce 'sudo apt install imagemagick' en la linea de " + 
              "comandos para instalarlo")
        program_logger.warning(warn)


def check_platform_updates():
    """Implementacion para detectar cambios que se hayan podido
    producir en los contenedores y bridges desde fuera del programa
    y actualizar las instancia guardadas en el registro. A partir 
    de las listas que proporciona lxc, se analiza si se han
    producido cambios que se deban actualizar en el programa"""    
    
    # Cambiamos el nvl del logger para que siempre se muestren los
    # warning
    root_logger = logging.getLogger()
    lvl = root_logger.level
    program_logger.debug(f" Nivel de logger establecido -> {lvl}")
    root_logger.level = logging.WARNING
    warned = False
    # Detecamos los cambios que se hayan producido fuera del programa
    # de los contenedores
    warned = _check_containers()
    # Detecamos los cambios que se hayan producido fuera del programa
    # de los bridge   
    warned = _check_bridges() or warned
    # Volvemos a poner el nvl de logger de antes y nos aseguramos que 
    # el usuario lea los warnings
    root_logger.level = lvl
    if warned:
        print("Se acaban de mostrar warnings importantes que pueden " + 
              "modificar el comportamiento del programa")
        input("Pulsa enter para proseguir con la ejecucion una vez se " + 
              "hayan leido ")

def _check_containers():
    warned = False
    cs_object = register.load(containers.ID)
    bgs = register.load(bridges.ID)
    if cs_object is None: return False
    
    process = subprocess.run(
        ["lxc", "list"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    cs_info = lxclist_as_dict(process.stdout.decode())
    headers = list(cs_info.keys())
    cs_updated = []
    for c in cs_object:
        if c.name not in cs_info[headers[0]]:
            warn = (f" El contenedor '{c.name}' se ha eliminado fuera " +
                    "del programa (informacion actualizada)")
            for bg in bgs:
                if c.name in bg.used_by:
                    bg.used_by.remove(c.name)
            program_logger.warning(warn)
            warned = True
            continue
        index = cs_info[headers[0]].index(c.name)
        if c.state != cs_info[headers[1]][index]:
            new_state = cs_info[headers[1]][index]
            warn = (f" El contenedor '{c.name}' se ha modificado desde " +
                   f"fuera del programa, ha pasado de '{c.state}' a " + 
                   f"'{new_state}' (informacion actualizada)")
            c.state = new_state
            program_logger.warning(warn)
            warned = True
        if c.state == "RUNNING":
            info = cs_info[headers[2]][index]
            current_nets = {}
            if info != "":
                if type(info) != list:
                    info = [info]
                for line in info:
                    splitted = re.split(r"\(| |\)", line)
                    while "" in splitted:
                            splitted.remove("")
                    ipv4, current_eth = splitted
                    current_nets[current_eth] = ipv4
            for eth, ip in c.networks.items():
                if eth not in current_nets:
                    warn = (f" La ethernet '{eth}' de '{c.name}' se ha " + 
                            "modificado desde fuera del programa o hay " + 
                            f"algun error ya que el contenedor esta " +
                            "arrancado pero lxc no muestra la conexion " +
                            "(informacion actualizada)")
                    c.connected_networks[eth] = False
                    program_logger.warning(warn)
                    warned = True
                else:
                    if ip not in current_nets.values():
                        new_ip = current_nets[eth]
                        warn = (f" La ip '{ip}' de la ethernet '{eth}' " +
                                f"del contenedor '{c.name}' se ha " +
                                f"modificado desde fuera del programa, ha " + 
                                f"pasado de {ip}:{eth} a {new_ip}:{eth} " +
                                "(informacion actualizada)")
                        c.networks[eth] = new_ip
                        program_logger.warning(warn)
                        warned = True
                    current_nets.pop(eth)
            for eth, ip in current_nets.items():
                warn = (f" Se ha añadido la tarjeta de red '{eth}' con " +
                        f"ip '{ip}' al contenedor '{c.name}' " + 
                         "(informacion actualizada)")
                c.add_to_network(eth, ip)
                c.connected_networks[eth] = True
                program_logger.warning(warn)
                warned = True
        cs_updated.append(c)
    if len(cs_updated) == 0:
        register.remove(containers.ID)
    else:
        register.update(containers.ID, cs_updated)
    register.update(bridges.ID, bgs)
    return warned

def _check_bridges():
    warned = False
    bgs = register.load(bridges.ID)
    if bgs is None: return False
    process = subprocess.run(
        ["lxc", "network", "list"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    bgs_info = lxclist_as_dict(process.stdout.decode())
    headers = list(bgs_info.keys())
    bgs_updated = []
    for bg in bgs:
        if bg.name not in bgs_info[headers[0]]:
            warn = (f" El bridge '{bg.name}' se ha eliminado desde " +
                    "fuera del programa (informacion actualizada)")
            program_logger.warning(warn)
            warned = True
            continue
        bgs_updated.append(bg)
    if len(bgs_updated) == 0:
        register.remove(bridges.ID)
    else:
        register.update(bridges.ID, bgs_updated)
    return warned
# --------------------------------------------------------------------  
