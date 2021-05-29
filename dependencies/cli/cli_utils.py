
import re
from math import ceil


def format_str(string:str, maxline_length:int=None, 
               indent:int=None, tripleq_mode=False) -> str:
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