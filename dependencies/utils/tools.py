
from math import floor, ceil
from contextlib import suppress

# -------------------------- HERRAMIENTAS ----------------------------
# --------------------------------------------------------------------
# Modulo en el que se definen funciones genericas y no relacionadas
# para que sean utilizadas por otros modulos
# -------------------------------------------------------------------- 

# --------------------------------------------------------------------        
def pretty(obj:object) -> str:
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
    dashes = ""
    names_line = ""
    values_line = ""
    
    prop = vars(obj)
    names = prop.keys()
    values = prop.values()
    max_lengths = []
    for name, val in zip(names, values):
        m = max(len(name), len(str(val)))
        dashes += "-"*(3 + m)
        max_lengths.append(m)
    dashes += "-"
    for name, value, mlength in zip(names, values, max_lengths):
        name_length = len(name)
        value_length = len(str(value))
        if name_length == mlength:
            dhalf = floor((mlength - value_length)/2)
            uhalf = ceil((mlength - value_length)/2)
            names_line += ("| " + name.upper() + 
                                " "*(mlength - name_length) + " ")
            values_line += ("| " + " "*dhalf + str(value) + 
                                                    " "*uhalf + " ")
        else:
            dhalf = floor((mlength - name_length)/2)
            uhalf = ceil((mlength - name_length)/2)
            names_line += ("| " +  " "*dhalf + name.upper() +
                                                    " "*uhalf + " ")
            values_line += ("| " + str(value) + 
                                " "*(mlength - value_length) + " ")
    names_line += "|"
    values_line += "|"
    string = (dashes + "\n" + names_line + "\n" + dashes + "\n" +
                                        values_line + "\n" + dashes)
    return string

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