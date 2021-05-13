
import logging
from math import floor
from logging import Logger
from time import time

# -------------------------- DECORADORES -----------------------------
# --------------------------------------------------------------------
# Modulo en el que se definen decoradores genericos y no relacionados
# para que sean utilizados por otros modulos
# -------------------------------------------------------------------- 

# --------------------------------------------------------------------
def timer(func):
    """Mide el tiempo que tarda en ejecutarse una funcion en minutos 
    y segundos

    Args:
        func: funcion a ejecutar
    """
    def f(*a, **ka):
        root_logger = logging.getLogger()
        t0 = time()
        func(*a,**ka)
        tf = time()
        if root_logger.level <= logging.WARNING:
            total_secs = round(tf-t0, 2)
            if total_secs < 60:
                print(f"Elapsed time: {total_secs} s")
            else: 
                mins = floor(total_secs/60)
                secs = int(total_secs - mins*60)
                print(f"Elapsed time: {mins} min {secs} s")
    return f

# -------------------------------------------------------------------- 
def catch_foreach(logger:Logger=None):
    """Ejecuta una funcion tantas veces como argumentos no opcionales
    se hayan pasado a la funcion y maneja las excepciones que puedan 
    surgir durante la ejecucion

    Args:
        logger (Logger, optional): logger con el que notificar los 
            errores que puedan surgir
    """
    def _catch_foreach(func):
        def catch (*args, **optionals):
            successful = []
            for a in args:
                try:
                    func(a, **optionals)
                    successful.append(a)
                except Exception as err:
                    if str(err) == "":
                        pass
                    elif logger == None:
                        print(f"ERROR:{err}")  
                    else:
                        logger.error(err)    
            return successful
        return catch
    return _catch_foreach

# -------------------------------------------------------------------- 