
import os
import re
import logging
import platform
import subprocess
from time import sleep
from functools import reduce
from math import floor

import program.controllers.bridges as bridges
import program.controllers.containers as containers
import dependencies.register.register as register
from dependencies.utils.tools import pretty, objectlist_as_dict

# --------------------- FUNCIONES DE PROGRAMA ------------------------
# --------------------------------------------------------------------
# Este fichero se encarga de proporcionar funciones especificas del
# programa. Define como se van a conectar los contenedores con 
# los bridges (quien con quien), realiza comprobaciones de entorno y 
# muestra informacion del programa -> su estado, estructura, etc.
# --------------------------------------------------------------------

class ProgramError(Exception):
    pass
# --------------------------------------------------------------------
program_logger = logging.getLogger(__name__)
# --------------------------------------------------------------------
def connect_machines():
    """ Se encarga de conectar los contenedores con los bridge. Mira 
    todos los contenedores creados (que estan en el registro) y si
    no se le ha asociado a ninguna network todavia lo conecta a una de
    las existentes dependiendo del tag que tenga (Los servidores a
    bridge 0, los clientes al bridge 1 y load balancer a los 2)"""
    
    # Si no hay puentes a los que conectar salimos
    bgs = objectlist_as_dict(
        register.load(bridges.ID),
        key_attribute="name"
    )
    if bgs == None: return
    # Si no hay vms creadas que conectar salimos
    cs = register.load(containers.ID)
    if cs == None: return
    
    j = 0
    existing_ips = []
    for c in cs:
        existing_ips += c.networks.values()
    for c in cs:
        # Si ya se ha conectado continuamos con la siguiente
        if len(c.networks) > 0: continue
        bridges_to_connect = []
        if c.tag == "server" or c.tag == "load balancer":
            if "lxdbr0" in bgs:
                bridges_to_connect.append(bgs['lxdbr0'])
        if c.tag == "client" or c.tag == "load balancer":
            if "lxdbr1" in bgs:
                bridges_to_connect.append(bgs['lxdbr1'])
        for b in bridges_to_connect:
            # Asiganamos una ip que no exista todavia
            ip = f"{b.ipv4_addr[:-4]}{j+10}"
            while ip in existing_ips:
                j += 1    
                ip = f"{b.ipv4_addr[:-4]}{j+10}"  
            existing_ips.append(ip)
            bridges.attach(c.name, to_bridge=b)
            containers.connect(
                c,
                with_ip=ip,
                to_network=b.ethernet
            )
        containers.configure_netfile(c)

def update_conexions():
    """Revisa si algun contenedor ha sido eliminado para 
    eliminarlo del bridge al que estaba asociado (bridge.used_by)"""
    bgs = register.load(register_id=bridges.ID)
    if bgs == None: return
    cs = register.load(register_id=containers.ID)
    if cs == None:
        names_existing_cs = []
    else:
        names_existing_cs = list(map(lambda c: c.name, cs))
    
    for b in bgs:
        deleted = []
        for c_name in b.used_by:
            if c_name not in names_existing_cs:
                deleted.append(c_name)
        for d in deleted:
            b.used_by.remove(d)
    register.update(bridges.ID, bgs)
    
# --------------------------------------------------------------------
def print_state():
    """Muestra por consola el estado de los objetos del programa 
    (contenedores y bridges)"""
    cs = register.load(register_id=containers.ID)
    bgs = register.load(register_id=bridges.ID)
    print("CONTENEDORES")
    if cs != None:
        for c in cs:
            print(pretty(c))
    else:
        print("No hay contenedores creados por el programa")
    print("BRIDGES")
    if bgs != None:       
        for b in bgs:
            print(pretty(b))
    else:
        print("No hay bridges creados por el programa")
        
def show_diagram():
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
        
def show_files_structure():
    """Muestra la estructura de ficheros utilizada para este proyecto
    y sus relaciones. Tambien muestra las dependencias externas a las
    que esta ligado"""
    try:
        path = "program/resources/images/files_structure.png"
        subprocess.Popen(
            ["display", path],
            stdout=subprocess.PIPE
        )
        path = "program/resources/images/external_dependencies.png"
        subprocess.Popen(
            ["display", path],
            stdout=subprocess.PIPE
        )
    except Exception as err:
        if "display" in str(err):
            program_logger.error("Se necesita instalar 'imagemagick'")
        else:
            program_logger.error(err)
    
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
    system = platform.system()
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


def check_updates():
    """Implementacion para detectar cambios que se hayan podido
    producir en los contenedores y bridges desde fuera del programa
    y actualizar las instancia guardadas en el registro. A partir 
    de las listas que proporciona lxc, se analiza si se han
    producido cambios que se deban actualizar en el programa"""    
    cs_object = register.load(containers.ID)
    bgs = register.load(bridges.ID)
    if cs_object is None: return
    # Cambiamos el nvl del logger para que siempre se muestren los
    # warning
    root_logger = logging.getLogger()
    lvl = root_logger.level
    program_logger.debug(f" Nivel de logger establecido -> {lvl}")
    root_logger.level = logging.WARNING
    warned = False
    # Detecamos los cambios que se hayan producido fuera del programa
    # de los contenedores
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
            warn = (f" El contenedor '{c.name}' se ha modificado fuera " +
                   f"del programa, ha pasado de '{c.state}' a " + 
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
                            "(informacion NO actualizada)")
                    program_logger.warning(warn)
                    warned = True
                else:
                    if ip not in current_nets.values():
                        new_ip = current_nets[eth]
                        warn = (f" La ip '{ip}' de la ethernet '{eth}' " +
                                f"del contenedor '{c.name}' se ha " +
                                f"modificado fuera del programa, ha pasado " + 
                                f"de {ip}:{eth} a {new_ip}:{eth} " +
                                "(informacion actualizada)")
                        c.networks[eth] = new_ip
                        program_logger.warning(warn)
                        warned = True
                    current_nets.pop(eth)
            for eth in current_nets:
                warn = (f" El contenedor '{c.name}' se ha conectado a otro " +
                           "bridge que no forma parte del programa " + 
                           "(informacion NO actualizada)")
                for bg in bgs:
                    if eth == bg.ethernet:
                        warn = (f" El contenedor '{c.name}' se ha conectado " +
                           f"a otro bridge que forma parte del programa " + 
                           f"'{bg.name}' (informacion actualizada)")
                        if c.name not in bg.used_by:
                            bg.used_by.append(c.name)
                        c.networks[eth] = current_nets[eth]
                        program_logger.warning(warn)
                        warned = True
                        break
                else:
                    program_logger.warning(warn)
                    warned = True
        cs_updated.append(c)
    if len(cs_updated) == 0:
        register.remove(containers.ID)
    else:
        register.update(containers.ID, cs_updated)
    # Detecamos los cambios que se hayan producido fuera del programa
    # de los bridge   
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
            warn = (f" El bridge '{bg.name}' se ha eliminado fuera " +
                    "del programa (informacion actualizada)")
            program_logger.warning(warn)
            continue
        bgs_updated.append(bg)
    register.update(bridges.ID, bgs_updated)
    # Volvemos a poner el nvl de logger de antes y nos aseguramos que 
    # el usuario lea los warnings
    root_logger.level = lvl
    if warned:
        print("Se acaban de mostrar warnings importantes que pueden " + 
              "modificar el comportamiento del programa")
        input("Pulsa enter para proseguir con la ejecucion una vez se " + 
              "hayan leido ")

# --------------------------------------------------------------------  
def lxc_list():
    """Se encarga de mostrar la lista de contenedores de lxc, pero 
    en caso de estar arrancados, como la ip tarda un rato en
    aparecer, la funcion espera a que se haya cargado toda la
    informacion para mostrar la lista. Comprueba que todas las ips
    hayan aparecido"""
    cs = register.load(containers.ID)
    program_logger.info(" Cargando resultados...")
    if cs == None:
        subprocess.call(["lxc", "list"]) 
        return
    running = list(filter(lambda c: c.state == "RUNNING", cs))
    frozen = list(filter(lambda c: c.state == "FROZEN", cs))
    total = running+frozen
    if len(total) == 0:
        subprocess.call(["lxc", "list"]) 
        return
    ips = reduce(lambda acum, c: acum+len(c.networks), total, 0)
    salida, t, twait, time_out= "", 0, 0.1, 10
    while not salida.count(".") == 3*ips:
        sleep(twait); t += twait
        if t >= time_out:
            program_logger.error(" timeout del comando 'lxc list'")
            return
        out = subprocess.Popen(["lxc", "list"], stdout=subprocess.PIPE) 
        salida = out.stdout.read().decode()
        salida = salida[:-1] # Eliminamos el ultimo salto de linea
    print(salida)

def lxc_network_list():
    """Muestra la network list de lxc (bridges creados)"""
    subprocess.call(["lxc", "network", "list"])
    
def lxclist_as_dict(string:str) -> dict:
    """Analiza una lista de lxc y proporciona toda su informacion 
    en forma de diccionario para que sea facilmente accesible.
    CUIDADO: Los headers de la lista dependen del idioma en el que
    este el ordenador anfitrion o del idioma usado de lxc (No 
    siempre son los mismos)

    Args:
        string (str): string que contiene la lista de lxc

    Returns:
        dict: diccionario con la informacion de la lista (los 
        headers son las claves del diccionario)
    """
    info = {}
    chars = list(string)
    colums = -1
    line_length = 0
    cells_length = []
    cell_start = 1
    # Calculamos la longitud de cada linea, la longitud de cada celda
    # y el numero de filas y columnas
    for i, c in enumerate(chars):
        if c == "|":
            break
        line_length = i + 1
        if c == "+":
            colums += 1 
            if colums > 0:
                cells_length.append(line_length-1-cell_start)
            cell_start = 1 + i
            continue
    rows = -1
    lines = int(len(chars)/line_length)
    for i in range(lines):
        if chars[i*line_length] == "+":
            rows += 1
    # Vamos mirando cada linea de cada columna y vemos si es 
    # una fila de guiones o es una fila con espacio en 
    # blanco => informacion
    _start = line_length + 1
    for i in range(colums):
        if i != 0:
            _start += cells_length[i-1] + 1
        _end = _start + cells_length[i] - 1
        key = string[_start:_end].strip()
        info[key] = []
        k = 0
        for j in range(rows):
            start = _start + line_length*(k+j+1) 
            while start < len(chars) and chars[start] == "-":
                start += line_length
            end = start + cells_length[i] - 1   
            values = []
            if start >= len(chars): continue
            # Miramos si hay mas de una linea seguida con 
            # informacion y con k recalibramos los siguientes
            # start de las siguientes lineas
            while chars[start] == " ":
                value = string[start:end].strip()
                values.append(value)
                if len(values) >= 1:
                    k += 1
                start += line_length
                end += line_length
            # Establecemos un criterio de devolucion de la
            # informacion para que luego sea mas facil de acceder
            # a esta en otras funciones
            if len(values) > 1:
                while "" in values:
                    values.remove("")
            if len(values) == 1:
                values = values[0]
            if len(values) == 0:
                values = ""
            info[key].append(values)
    return info

# --------------------------------------------------------------------