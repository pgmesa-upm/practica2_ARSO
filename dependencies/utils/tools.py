
from math import floor, ceil
from contextlib import suppress
from re import sub


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

    Args:
        obj (object): objeto cuyos atributos se quieren pasar a 
            formato tabla

    Returns:
        str: Tabla con los atributos del objeto
    """
    attr_dict = vars(obj)
    attr_colums = list(attr_colums)
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
    table_dict = {}; dash = "-"; rows = 1
    for i, colum in enumerate(attr_colums):
        colum_max_length = 0
        if len(colum) > rows: rows = len(colum)
        for attr in colum:
            row_max_length = len(attr)
            try:
                attr_val_length = len(str(attr_dict[attr]))
            except:
                colum.remove(attr)
            if attr_val_length > row_max_length:
                row_max_length = attr_val_length
            if row_max_length > colum_max_length:
                colum_max_length = row_max_length
        table_dict[i+1] = {
            "colum": colum,
            "maxc_length": colum_max_length
        }
        dash += "-"*(colum_max_length + 3)
          
    def center_cell(string, mlength, upper=False, border=True):
        """Devuelve una linea con el string centrado en una celda
        dependiendo de la longitud maxima que puede tener el string 
        en la celda. Se usa un espacio entre cada -> '|'. Ej: | string 

        Args:
            string ([type]): string a centrar en la celda
            mlength ([type]): maxima longitud de un string que va a 
                haber en esa columna
            upper (bool, optional): para poner el string en mayusculas
                (Para los Headers)

        Returns:
            [type]: [description]
        """
        str_length = len(string)
        brd = "  "
        if upper: string = string.upper()
        if border: brd = "| "
        if str_length == mlength:
            return (brd + string + " "*(mlength - str_length) + " ")
        else:
            dhalf = floor((mlength - str_length)/2)
            uhalf = ceil((mlength - str_length)/2)
            return (brd +  " "*dhalf + string + " "*uhalf + " ")
        
    # Creamos las lineas de atributos y valores de cada fila    
    table_str = dash
    for i in range(rows):
        attrs_line = ""
        values_line = ""
        subdash = "-"
        last_empty = False
        for j, colum in enumerate(table_dict.values()):
            right_border = True
            left_border = True
            last = j == len(table_dict.values()) - 1
            mlength = colum["maxc_length"]
            try:
                right_border = True
                left_border = True
                attr = colum["colum"][i]
                value = str(attr_dict[attr])
                attr_cell = center_cell(attr, mlength, upper=True)
                value_cell = center_cell(value, mlength)
                attrs_line += attr_cell
                values_line += value_cell
                subdash += "-"*len(attr_cell)
                last_empty = False
            except IndexError:
                attr = ""
                value = ""
                if j == 0 or last_empty: left_border = False
                if last or last_empty: right_border = False
                attr_cell = center_cell(
                    attr, mlength, 
                    upper=True, border=left_border
                )
                value_cell = center_cell(
                    value, mlength, 
                    border=left_border
                )
                attrs_line += attr_cell
                values_line += value_cell
                if j == 0: subdash = " "*(len(attr_cell)) + "-"
                elif last: subdash += " "*len(attr_cell)
                elif last_empty:
                    subdash = subdash[:-1]
                    subdash += " "*(len(attr_cell))
                else: subdash += " "*(len(attr_cell)-1) + "-"
                last_empty = True
        block = f"\n{attrs_line}|\n{subdash}\n{values_line}|\n{subdash}"
        if not right_border:        
            block = f"\n{attrs_line}\n{subdash}\n{values_line}\n{subdash}"
        table_str += block
    return table_str

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