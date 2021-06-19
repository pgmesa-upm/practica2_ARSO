
from math import floor, ceil
from contextlib import suppress
import re
import copy

# -------------------------- HERRAMIENTAS ----------------------------
# --------------------------------------------------------------------
# Modulo en el que se definen funciones genericas y no relacionadas
# para que sean utilizadas por otros modulos
# -------------------------------------------------------------------- 

# --------------------------------------------------------------------        
def pretty(obj:object, *attr_colums, firstcolum_order:list=None) -> str:
    """Devuelve los atributos de un objeto en forma de string. (Como
    una tabla ordenada) 
    ej:
        Container("s1", STTOPPED) -> 
        ------------------
        | NAME |  STATE  | ...
        ------------------
        |  S1  | STOPPED | ...
        ------------------
            .       .
            .       .
            .       .

    Args:
        obj (object): objeto cuyos atributos se quieren pasar a 
            formato tabla

    Returns:
        str: Tabla con los atributos del objeto
    """
    attr_dict = vars(obj)
    # Pasamos a strings los valores del diccionario
    for attr, attr_val in attr_dict.items(): 
        attr_dict[attr] = str(attr_val)
    attr_colums = list(attr_colums)
    # Comprobamos que las tuplas que nos han pasado son correctas
    valid_colums = []
    all_checked_attrs = []
    for colum in attr_colums:
        checked_attrs = []
        for attr in colum:#
            # Miramos si el atributo existe
            if attr_dict.get(attr, None) is None:
                continue
            # Miramos si el atributo nos lo han pasado repetido
            if attr in checked_attrs or attr in all_checked_attrs:
                continue
            checked_attrs.append(attr)
        if not len(checked_attrs) == 0:
            valid_colums.append(tuple(checked_attrs))
            all_checked_attrs += checked_attrs
    attr_colums = valid_colums  
    # Vemos para que tuplas no nos han pasado pareja
    singles = []
    for name in attr_dict:
        for c in attr_colums:
            if name in c:
                break
        else:
            singles.append((name,))
    attr_colums += singles
    # Ordenamos las tuplas segun nos lo especifiquen
    ordered = []
    if firstcolum_order is not None:
        for attr in firstcolum_order:
            for colum in attr_colums:
                if attr in colum[0] and colum not in ordered:
                    ordered.append(colum)
                    break
    for c in ordered:
        if c in attr_colums:
            attr_colums.remove(c)
    attr_colums = ordered + attr_colums
    # Guardamos en un diccionario, las columnas de atributos numeradas
    # y la maxima longitud del atributos o valor mas grande que va a 
    # haber en la columna. Tambien creamos la linea de guiones "-" de 
    # la fila principal
    incorrect_colums = []
    table_dict = {}; dash = "-"; rows = 1
    for i, colum in enumerate(attr_colums):
        colum_max_length = 0
        if len(colum) > rows: rows = len(colum)
        for attr in colum:
            row_max_length = len(attr)
            attr_val_length = len(str(attr_dict[attr]))
            if attr_val_length > row_max_length:
                row_max_length = attr_val_length
            if row_max_length > colum_max_length:
                colum_max_length = row_max_length
        table_dict[i+1] = {
            "colum": colum,
            "maxc_length": colum_max_length
        }
        dash += "-"*(colum_max_length + 3)
    map(lambda colum: attr_colums.remove(colum), incorrect_colums)
    def center_cell(string:str, mlength:int, upper:bool=False,
                    left_border:bool=True, right_border:bool=True):
        """Devuelve una linea con el string centrado en una celda
        dependiendo de la longitud maxima que puede tener el string 
        en la celda. Se usa un espacio entre cada -> '|'. Ej: | string | 

        Args:
            string ([type]): string a centrar en la celda
            mlength ([type]): maxima longitud de un string que va a 
                haber en esa columna
            upper (bool, optional): para poner el string en mayusculas
                (Para los Headers)

        Returns:
            str: Devuelve la celda con el valor centrado y con bordes
                en caso de que no se especifique lo contrario
        """
        str_length = len(string)
        leftb = " "
        rightb = " "
        if upper: string = string.upper()
        if left_border: leftb = "| "
        if right_border: rightb = " |"
        if str_length == mlength:
            return (leftb + string + " "*(mlength - str_length) + rightb)
        else:
            dhalf = floor((mlength - str_length)/2)
            uhalf = ceil((mlength - str_length)/2)
            return (leftb +  " "*dhalf + string + " "*uhalf + rightb)
        
    # Creamos las lineas de atributos y valores de cada fila    
    table_str = dash
    for i in range(rows):
        attrs_line = ""
        values_line = ""
        subdash = ""
        last_empty = False
        for j, colum in enumerate(table_dict.values()):
            is_first_colum = j == 0
            mlength = colum["maxc_length"]
            try:
                # Celda llena
                left_border = True
                if not last_empty and not is_first_colum:
                    left_border = False
                attr = colum["colum"][i]
                value = str(attr_dict[attr])
                attr_cell = center_cell(
                    attr, mlength, 
                    upper=True,
                    left_border=left_border
                )
                value_cell = center_cell(
                    value, mlength,
                    left_border=left_border
                )
                attrs_line += attr_cell
                values_line += value_cell
                subdash += "-"*len(attr_cell)
                last_empty = False
            except IndexError:
                # Celda vacia 
                void_cell = center_cell(
                    "", mlength,
                    upper=True, 
                    left_border=False,
                    right_border=False
                )
                subdash += " "*(len(void_cell))
                if is_first_colum or last_empty:
                    subdash += " "; void_cell += " "
                attrs_line += void_cell; values_line += void_cell
                last_empty = True 
        block = f"\n{attrs_line}\n{subdash}\n{values_line}\n{subdash}"
        table_str += block
    return table_str

# def pretty_fusion(*pretty_str) -> str:
#     fusion = ""
#     for i, string in enumerate(pretty_str):
#         last = i == len(pretty_str) - 1
#         index = len(string) - 1
#         if not last:
#             char = string[index]
#             while char != "\n":
#                 index -= 1
#                 char = string[index]
#         fusion += string[:index]
#     return fusion

# --------------------------------------------------------------------
def format_str(string:str, maxline_length:int=None, 
               indent:int=None, tripleq_mode=False) -> str:
    # -------------------------------
    # Añadir comprobaciones de que lo que me han pasado
    # es correcto ------- y añadir que los espacios cuenten como 
    # espacio ocupado en la linea

    # Configuramos el modo del string
    reg_expression = " "
    if tripleq_mode:
        reg_expression = " |\n|\r"
    splitted = re.split(reg_expression, string)
    filtered = ""
    for i, w in enumerate(splitted):
        last = i == len(splitted) - 1
        if w != "":
            if last:
                filtered += w 
            else:
                filtered += w + " "
    string = filtered
    # Miramos la tabulacion de cada linea
    if indent is None:
        spaces = ""
    else:
        spaces = " "*indent
    # Formateamos el string
    formatted_string = spaces
    if maxline_length is not None:
        start_index = 0
        final_index = 0
        maxline_length -= indent
        # Vemos las segmentaciones que vamos a hacer del string
        # segun la longitud especificada de cada linea y los 
        # espacios de inicio de cada una
        # Formateamos cada linea
        while True:
            final_index += maxline_length
            if final_index >= len(string):
                line = string[start_index:]
                formatted_string += line
                break
            for _ in range(maxline_length):
                char = string[final_index]
                if char == " " or char == "\n":
                    break
                final_index -= 1
            if start_index == final_index:
                final_index += maxline_length
            line = string[start_index:final_index] + "\n" + spaces
            formatted_string += line
            start_index = final_index + 1
        return formatted_string

# --------------------------------------------------------------------
def objectlist_as_dict(l:list, key_attribute:str) -> dict:
    """Devuelve una lista que contiene objetos de la misma clase en 
    forma de diccionario, utilizando como clave un atributo del objeto
    ej:
        [obj1] -> {obj1.key_attribute: obj1}

    Args:
        l (list): lista de objetos a convertir
        key_attribute (str): atributo del objeto que se usara como 
            clave

    Returns:
        dict: diccionario con los objetos de la lista como valores y 
            el atributo especificado como clave de cada objeto
    """
    if l == None: return None
    dic = {}
    for obj in l:
        with suppress(Exception):
            dic[getattr(obj, key_attribute)] = obj
    return dic

# --------------------------------------------------------------------   
def concat_array(array:list, separator:str=",") -> str:
    """Concatena los elementos de un array y devuelve un unico string
        ej:
        [Obj1(name="Pepe"), Obj2(name="Luis")] y  __str__ = self.name
        --> return "Pepe, Luis" 
        
    Args:
        array (list): lista a concatenar
        separator (str, optional): simbolo que se quiere usar para 
            separar cada elemento de la lista

    Returns:
        str: string que contiene la lista concatenada
    """
    c = ""
    for i, obj in enumerate(array):
        if i == len(array) - 1:
            c += str(obj)
        else:
            c += str(obj) + separator + " "
    return c
   
# --------------------------------------------------------------------
def remove_many(remove_in:list, *remove):
    """Intenta eliminar de una lista todos los elementos que se
    especifiquen en remove. Si el elemento no existe se ignora

    Args:
        remove_in (list): lista de la que se quieren eliminar varios
            elementos
    """
    for r in remove:
        with suppress(Exception):
            remove_in.remove(r)

# --------------------------------------------------------------------
def remove_ntimes(array:list, *elements_to_remove, times:int=None):
    if times == None: times = -1
    array_cp = copy.deepcopy(array)
    for elem in elements_to_remove:
        removed = 0
        for elem_arr in array_cp:
            if removed == times:
                break
            if elem == elem_arr:
                array.remove(elem_arr)
                removed += 1
        