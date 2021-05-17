
import subprocess
from time import sleep
import re
import json


_lxc_list_formats = ["table", "csv", "json", "yaml"]
# --------------------------------------------------------------------
class LxcError(Exception):
    """Excepcion personalizada para los errores al manipular 
    contenedores de lxc"""
    pass

# --------------------------------------------------------------------
class LxcNetworkError(Exception):
    """Excepcion personalizada para los errores al manipular 
    bridges de lxc"""
    pass

# --------------------------------------------------------------------
def run(cmd:list, stdout=True, stderr=True):
    """Ejecuta un comando mediante subprocess y controla los 
    errores que puedan surgir. Espera a que termine el proceso
    (Llamada bloqueante)

    Args:
        cmd (list): Comando a ejecutar

    Raises:
        LxcError: Si surge algun error ejecutando el comando
        LxcNetworkError: Si surge algun error ejecutando en comando
            relacioneado con los bridge (networks)
    """
    options = {}
    if stdout:
        options["stdout"] = subprocess.PIPE
    options["stderr"] = subprocess.PIPE
    process = subprocess.run(cmd, **options)
    outcome = process.returncode
    if outcome != 0:
        err_msg = f" Fallo al ejecutar el comando {cmd}"
        if stderr:
            err = process.stderr.decode()
            err_msg += f"\n Mensaje de error de lxc: -> {err}"
        elif stdout:
            err_msg = process.stdout.decode()
        if "network" in cmd:
            raise LxcNetworkError(err_msg)
        raise LxcError(err_msg)
    if stdout:
        return process.stdout.decode()

def Popen(cmd:list):
    """Ejecuta un comando mediante subprocess no bloqueante (
        no espera a que acabe de ejecutarse)

    Args:
        cmd (list): Comando a ejecutar
    """
    subprocess.Popen(cmd)
# --------------------------------------------------------------------
# --------------------------------------------------------------------
def _lxc_generic_list(cmd:list, print_:bool=False, 
                                print_format:str="table"):
    if print_format not in _lxc_list_formats:
        raise LxcError(f" El formato {print_format} no es valido")
    out = run(cmd + ["--format", print_format])
    out = out[:-1]
    if print_:
        if print_format == "json":
            json_list = json.loads(out)
            out = json.dumps(json_list, indent=4, sort_keys=True)
        print(out)
    # Devuelve una lista con la informacion de cada imagen en
    # forma de diccionario
    table = run(cmd)
    return process_lxctable(table)

def lxc_list(print_:bool=False, print_format:str="table",
                        ips_to_wait:int=0, time_out:int=10):
    """Se encarga de mostrar la lista de contenedores de lxc, pero 
    en caso de estar arrancados, como la ip tarda un rato en
    aparecer, la funcion espera a que se haya cargado toda la
    informacion para mostrar la lista. Comprueba que todas las ips
    hayan aparecido"""
    cmd = ["lxc", "list"]
    if ips_to_wait > 0:
        out, t, twait= "", 0, 0.1
        while not out.count(".") == 3*ips_to_wait:
            sleep(twait); t += twait
            if t >= time_out:
                err = (" timeout de 'lxc list', no se pudieron " + 
                        "cargar todas las ips")
                raise LxcError(err)
            out = run(cmd) 
    dic = _lxc_generic_list(
        cmd,
        print_=print_, 
        print_format=print_format
    )
    # Cambiamos la forma de presentar el diccionario
    headers = list(dic.keys())
    my_headers = ["NAME", "STATE", "IPV4", "IPV6", "TYPE", "SNAPSHOTS"]
    rearranged_dict = {}
    keys = dic[headers[0]] # Nombres de contenedores seran las claves
    if len(keys) > 0: 
        for i, k in enumerate(keys):
            new_page = {}
            for j, h in enumerate(headers):
                new_page.update({my_headers[j]: dic[h][i]})
            rearranged_dict.update({k: new_page})
    # Modificamos la forma de presentar las networks ipv4
    for name in rearranged_dict:
        info = rearranged_dict[name]["IPV4"]
        nets = {}
        if info != "":
            if type(info) != list:
                info = [info]
            for line in info:
                splitted = re.split(r"\(| |\)", line)
                while "" in splitted:
                        splitted.remove("")
                ipv4, current_eth = splitted
                nets[current_eth] = ipv4
        rearranged_dict[name]["IPV4"] = nets
    return rearranged_dict
    
def lxc_network_list(print_=False, print_format="table"):
    """Muestra la network list de lxc (bridges creados)"""
    dic = _lxc_generic_list(
        ["lxc", "network", "list"],
        print_=print_, 
        print_format=print_format
    )
    # Cambiamos la forma de presentar el diccionario
    headers = list(dic.keys())
    my_headers = ["NAME", "TYPE", "MANAGED", "DESCRIPTION", "USED BY"]
    rearranged_dict = {}
    keys = dic[headers[0]] # Nombres de contenedores seran las claves
    if len(keys) > 0: 
        for i, k in enumerate(keys):
            new_page = {}
            for j, h in enumerate(headers):
                new_page.update({my_headers[j]: dic[h][i]})
            rearranged_dict.update({k: new_page})
    return rearranged_dict

def lxc_image_list(print_=False, print_format="table"):
    dic = _lxc_generic_list(
        ["lxc", "image", "list"],
        print_=print_, 
        print_format=print_format
    )
    # Cambiamos la forma de presentar el diccionario
    headers = list(dic.keys())
    my_headers = ["ALIAS", "FINGERPRINT", "PUBLIC", "DESCRIPTION",
                  "ARCHITECTURE", "TYPE", "SIZE", "UPLOAD DATE"]
    rearranged_dict = {}
    keys = dic[headers[1]] # Nombres de contenedores seran las claves
    if len(keys) > 0: 
        for i, k in enumerate(keys):
            new_page = {}
            for j, h in enumerate(headers):
                new_page.update({my_headers[j]: dic[h][i]})
            rearranged_dict.update({k: new_page})
    return rearranged_dict
    
# --------------------------------------------------------------------   
def process_lxctable(string:str) -> dict:
    """Analiza una lista de lxc y proporciona toda su informacion 
    en forma de diccionario para que sea facilmente accesible.
    CUIDADO: Los headers de la lista dependen del idioma en el que
    este el ordenador anfitrion o del idioma usado de lxc (No 
    siempre son los mismos). Devuelve un diccionario del tipo:
    {NAME: [s1,s2,s3, ...], STATE: [RUNNING, STOPPED, ...]} 

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