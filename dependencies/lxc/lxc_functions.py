
import subprocess
from time import sleep

def checkin_lxclist(list_cmd:list, colum:int, val:str):
    process = subprocess.run(
        list_cmd,
        stdout=subprocess.PIPE
    )
    table = process_lxclist(process.stdout.decode())
    headers = list(table.keys())
    if val in table[headers[colum]]:
        return True
    return False

def lxc_list(ips_to_wait:int=0, time_out=10, print_=False):
    """Se encarga de mostrar la lista de contenedores de lxc, pero 
    en caso de estar arrancados, como la ip tarda un rato en
    aparecer, la funcion espera a que se haya cargado toda la
    informacion para mostrar la lista. Comprueba que todas las ips
    hayan aparecido"""
    if ips_to_wait == 0:
        p = subprocess.run(["lxc", "list"], stdout=subprocess.PIPE)
        salida = p.stdout.decode()
    else:
        salida, t, twait= "", 0, 0.1
        while not salida.count(".") == 3*ips_to_wait:
            sleep(twait); t += twait
            if t >= time_out:
                err = (" timeout de 'lxc list', no se pudieron " + 
                        "cargar todas las ips")
                raise Exception(err)
            out = subprocess.Popen(
                ["lxc", "list"], 
                stdout=subprocess.PIPE
            ) 
            salida = out.stdout.read().decode()
            salida = salida[:-1] # Eliminamos el ultimo salto de linea
    if print_:
        print(salida)
    return salida

def lxc_image_list(print_=False):
    l = subprocess.run(
        ["lxc", "image", "list"],
        stdout=subprocess.PIPE
    )
    out = l.stdout.decode()[:-1]
    if print_:
        print(out)
    return out

def lxc_network_list(print_=False):
    """Muestra la network list de lxc (bridges creados)"""
    l = subprocess.run(
        ["lxc", "network", "list"],
        stdout=subprocess.PIPE
    )
    out = l.stdout.decode()[:-1]
    if print_:
        print(out)
    return out
    
def process_lxclist(string:str) -> dict:
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