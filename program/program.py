
from time import sleep
from typing import Container
from program.platform.machines import load_balancer, servers
from dependencies.utils.tools import pretty
from contextlib import suppress
import logging
import platform as plt
import subprocess

from dependencies.lxc import lxc
from program.controllers import containers, bridges
from dependencies.register import register

# --------------------- FUNCIONES DE PROGRAMA ------------------------
# --------------------------------------------------------------------
# Este fichero se encarga de proporcionar funciones especificas del
# programa. Realiza comprobaciones de entorno (revisa dependencias, si 
# ha habido cambios en los elementos de la plataforma desde fuera del
# programa, etc)
# --------------------------------------------------------------------

class ProgramError(Exception):
    pass

class Dependency:
    def __init__(self, name:str, cmd_to_check:str, 
                 cmd_to_install:str, type_:str):
        self.name = name
        self.check_cmd = cmd_to_check
        self.cmd = cmd_to_install
        self.type = type_
    
    def check(self) -> bool:
        try:
            subprocess.run(
                self.check_cmd.split(" "),
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE
            )
            self.installed = True
        except:
            self.installed = False
        return self.installed
    
    def __str__(self) -> str:
        return self.name
# --------------------------------------------------------------------
program_logger = logging.getLogger(__name__)
_dependencies = {}
# --------------------------------------------------------------------
def show_platform_diagram():
    """Muestra un diagrama que explica la finalidad del programa"""
    if not _dependencies["imagemagick"].check():
        program_logger.error("Se necesita instalar 'imagemagick'")
        return
    path = "program/resources/images/diagram.png"
    subprocess.Popen(["display", path], stdout=subprocess.PIPE) 
        
def show_dependencies():
    """Muestra las dependencias externas a las que esta ligado el
    programa"""
    for d in _dependencies.values():
        d.check()
        print(pretty(d))

# --------------------------------------------------------------------
def list_lxc_containers(*cs:Container):
    if logging.getLogger().level >= 40: return
    program_logger.info(" Cargando resultados...")
    running = list(filter(lambda c: c.state == "RUNNING", cs))
    frozen = list(filter(lambda c: c.state == "FROZEN", cs))
    total = running+frozen
    finished = False; timeout = False
    tf = 10; t = 0; twait = 0.1
    while not finished:
        if timeout:
            err = (" timeout de 'lxc list', no se pudieron " + 
                    "cargar todas las ips")
            program_logger.error(err)
            return
        cs_list = lxc.lxc_list()
        for c in total:
            for net in c.networks:
                if net not in cs_list[c.name]["IPV4"]:
                    break
            else:
                continue
            break
        else:
            finished = True
        sleep(twait); t += twait
        if t >= tf:
            timeout = True
    table = lxc.lxc_list(as_str=True)
    cs_names = list(map(str, cs))
    filtered_table = lxc.filter_lxc_table(table, *cs_names)
    if filtered_table != "":
        print(filtered_table)   

def list_lxc_bridges(*bgs):
    if logging.getLogger().level >= 40: return
    table = lxc.lxc_network_list(as_str=True)
    bg_names = list(map(str, bgs))
    filtered_table = lxc.filter_lxc_table(table, *bg_names)
    if filtered_table != "":
        print(filtered_table) 

# --------------------------------------------------------------------   
def check_dependencies():
    global _dependencies
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
    lxd = Dependency(
        "lxd", 
        "lxd --version", 
        "sudo apt install lxd",
        "mandatory"
    )
    xterm = Dependency(
        "xterm", 
        "xterm --version", 
        "sudo apt install xterm",
        "optional"
    )
    imagemagick = Dependency(
        "imagemagick", 
        "convert --version", 
        "sudo apt install imagemagick",
        "optional"
    )
    _dependencies[lxd.name] = lxd
    _dependencies[xterm.name] = xterm
    _dependencies[imagemagick.name] = imagemagick
    
    info = ("\nIntroduce 'show dep' para obtener informacion detallada " +
            "sobre las dependencias externas del programa")
    if not lxd.check():
        err = (" 'lxd' no esta instalado en este ordenador y es " +
               "necesario para la ejecucion del programa.\nIntroduce " +
               f"'{lxd.cmd}' en la linea de comandos para instalarlo")
        raise ProgramError(err + info)
    lxc.run(["lxd", "init", "--auto"])
    if not xterm.check():
        warn = (" 'xterm' no esta instalado en este ordenador y " +
               "algunas funcionalidades pueden requerir este modulo. " + 
              f"Introduce '{xterm.cmd}' en la linea de comandos para " + 
               "instalarlo")
        program_logger.warning(warn + info)
    if not imagemagick.check():
        warn = (" 'imagemagick' no esta instalado en este ordenador y " +
              "algunas funcionalidades pueden requerir este modulo. " + 
              f"Introduce '{imagemagick.cmd}' en la linea de comandos" + 
              "para instalarlo")
        program_logger.warning(warn + info)

def check_platform_updates():
    """Implementacion para detectar cambios que se hayan podido
    producir en los contenedores y bridges desde fuera del programa
    y actualizar las instancia guardadas en el registro. A partir 
    de las listas que proporciona lxc, se analiza si se han
    producido cambios que se deban actualizar en el programa""" 
    with suppress(Exception):
        register.add("updates", {})
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
    cs_info = lxc.lxc_list()
    cs_updated = []
    for c in cs_object:
        c.refresh()
        if c.name not in cs_info:
            warn = (f" El contenedor '{c.name}' se ha eliminado fuera " +
                    "del programa (informacion actualizada)")
            for bg in bgs:
                if c.name in bg.used_by:
                    bg.used_by.remove(c.name)
            program_logger.warning(warn)
            warned = True
            # Registramos cambios en contenedores
            register.update(
                "updates", True, override=False, dict_id="cs_num"
            )
            register.update(
                "updates", True, override=False, dict_id="cs_state"
            ) 
            if c.tag == servers.TAG:
                # Registramos que ha habido cambio en el numero de servidores
                # y hay que actualizar haproxy
                register.update(
                    "updates", True, override=False, dict_id="s_num"
                )
                # Como para hacer delete hay que parar, tambien cambia el estado
                register.update(
                    "updates", True, override=False, dict_id="s_state"
                ) 
            continue
        if c.state != cs_info[c.name]["STATE"]:
            new_state = cs_info[c.name]["STATE"]
            warn = (f" El contenedor '{c.name}' se ha modificado desde " +
                   f"fuera del programa, ha pasado de '{c.state}' a " + 
                   f"'{new_state}' (informacion actualizada)")
            c.state = new_state
            program_logger.warning(warn)
            warned = True
            # Registramos cambios en contenedores
            register.update(
                "updates", True, override=False, dict_id="cs_state"
            )
            if c.tag == servers.TAG:
                register.update(
                    "updates", True, override=False, dict_id="s_state"
                )
        if c.state == "RUNNING":
            current_nets = cs_info[c.name]["IPV4"]
            for eth, ip in c.networks.items():
                if eth not in current_nets:
                    warn = (f" La tarjeta de red '{eth}' de '{c.name}' " + 
                            "se ha modificado desde fuera del programa o " + 
                            f"hay algun error ya que el contenedor esta " +
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
                c.add_to_network(eth, with_ip=ip)
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
    bgs_info = lxc.lxc_network_list()
    bgs_updated = []
    for bg in bgs:
        if bg.name not in bgs_info:
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
