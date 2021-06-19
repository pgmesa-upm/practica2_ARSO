
import subprocess
from time import sleep
import re
import json
import csv


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
def run(cmd:list, stdout=True, stderr=True) -> str:
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
            err = process.stderr.decode()[:-1]
            err_msg += f"\nMensaje de error de lxc: -> {err}"
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
                        format_:str="table", as_str=False) -> dict:
    if format_ not in _lxc_list_formats:
        raise LxcError(f" El formato {format} no es valido")
    out = run(cmd + ["--format", format_])
    out = out[:-1]
    if print_:
        if format_ == "json":
            json_list = json.loads(out)
            out = json.dumps(json_list, indent=4, sort_keys=True)
        print(out)
    # Devuelve una lista con la informacion de cada imagen en
    # forma de diccionario
    if as_str:
        return out
    else:
        csv = run(cmd + ["--format", "csv"])
        return _process_lxccsv(csv)

def lxc_list(print_:bool=False, format_:str="table", as_str=False) -> dict:
    """Se encarga de mostrar la lista de contenedores de lxc, pero 
    en caso de estar arrancados, como la ip tarda un rato en
    aparecer, la funcion espera a que se haya cargado toda la
    informacion para mostrar la lista. Comprueba que todas las ips
    hayan aparecido"""
    cs_infolist = _lxc_generic_list(
        ["lxc", "list"],
        print_=print_, 
        format_=format_,
        as_str=as_str
    )
    if as_str: return cs_infolist
    # Cambiamos la forma de presentar el diccionario
    cs_infodict= {}
    headers = ["NAME", "STATE", "IPV4", "IPV6", "TYPE", "SNAPSHOTS"]
    for c_info in cs_infolist:
        cs_infodict[c_info[0]] = dict(zip(headers, c_info))
    # Modificamos la forma de presentar las networks ipv4
    for name in cs_infodict:
        info = cs_infodict[name]["IPV4"]
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
        cs_infodict[name]["IPV4"] = nets
    return cs_infodict
    
def lxc_network_list(print_=False, format_="table", as_str=False) -> dict:
    """Muestra la network list de lxc (bridges creados)"""
    bgs_infolist = _lxc_generic_list(
        ["lxc", "network", "list"],
        print_=print_, 
        format_=format_,
        as_str=as_str
    )
    if as_str: return bgs_infolist
    # Cambiamos la forma de presentar el diccionario
    bgs_infodict= {}
    headers = ["NAME", "TYPE", "MANAGED", "DESCRIPTION", "USED BY"]
    for b_info in bgs_infolist:
        bgs_infodict[b_info[0]] = dict(zip(headers, b_info))
    return bgs_infodict
    

def lxc_image_list(print_=False, format_="table", as_str=False) -> dict:
    image_infolist = _lxc_generic_list(
        ["lxc", "image", "list"],
        print_=print_, 
        format_=format_,
        as_str=as_str
    )
    if as_str: return image_infolist 
    # Cambiamos la forma de presentar el diccionario
    images_infodict= {}
    headers = ["ALIAS", "FINGERPRINT", "PUBLIC", "DESCRIPTION",
                    "ARCHITECTURE", "TYPE", "SIZE", "UPLOAD DATE"]
    for im_info in image_infolist:
        images_infodict[im_info[1]] = dict(zip(headers, im_info))
    return images_infodict

def filter_lxc_table(table, *elements):
    splitted = table.split("\n")
    def is_dash_line(string) -> bool:
        for i in range(len(string)):
            char = string[i]
            if char != "-" and char != "+":
                break
        else:
            return True
        return False
    dash_line = splitted.pop(0)
    headers = splitted.pop(0)
    valid_rows = []
    last_was_dash = True
    last_was_valid = False
    for line in splitted:
        if is_dash_line(line):
            last_was_dash = True
            last_was_valid = False
            continue
        for elem in elements:
            if " " + elem + " " in line:
                valid_rows.append(line)
                last_was_valid = True
                break
        else:
            if not last_was_dash and last_was_valid:
                valid_rows.append(None)
                valid_rows.append(line)
                last_was_valid = True
        last_was_dash = False
    filtered_table = f"{dash_line}\n{headers}\n{dash_line}"
    if len(valid_rows) == 0: return ""
    for valid in valid_rows:
        if valid is None:
            lenght = len(filtered_table) - len(dash_line) - 1
            filtered_table = filtered_table[:lenght]
        else:
            filtered_table += f"\n{valid}\n{dash_line}"
    return filtered_table
    
# --------------------------------------------------------------------   
def _process_lxccsv(string:str) -> list:
    """Procesa un string csv devuelto por lxc.
    
     - NOTAS del csv que devuelve lxc:
    Las celdas de mas de un elemento vienen con
    un salto de linea entre elementos, no hay comas dentro, y el conjunto
    viene entre comillas. Los cambios de linea del csv se marcan
    con un salto de linea. Los strings de mas de una palabra 
    vienen entre comillas (cuidado al hacer .split(",") si el string
    tiene comas dentro, se fragmentara la celda).

    Args:
        string (str): csv a procesar

    Returns:
        list: Lista con las filas del documento csv
    """
    start = 0; mark = "#;#"; index = 0; pairs = []
    while True:
        for _ in range(2):
            substring = string[start:]
            index = substring.find('"')
            start += index + 1
            pairs.append(start)
        if index == -1:
            break
        part_to_change = string[pairs[0]:pairs[1]-1]
        new_part = part_to_change.replace(",", mark)
        string = string.replace(part_to_change, new_part)
        start += len(mark)
        pairs = [] 
    first_division = string.split(",")
    rows = []
    row = []
    for elem in first_division:
        # Procesamos las celdas con mas de un elemento
        if '"' in elem and mark not in elem:
            elem = re.split("\"|\n", elem)[1:-1]
        # Procesamos los cambios de fila
        elif "\n" in elem:
            row_last_elem, elem = elem.split("\n")
            if mark in row_last_elem:
                row_last_elem = row_last_elem.replace(mark, ",")
                row_last_elem = row_last_elem.replace('"', "")
            if mark in elem:
                elem = elem.replace(mark, ",")
                elem = elem.replace('"', "")
            row.append(row_last_elem)
            rows.append(row)
            row = []
        row.append(elem)
    return rows

def _process_lxctable(string:str) -> dict:
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