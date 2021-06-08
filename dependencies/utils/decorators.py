
import logging
from math import floor
from logging import Logger
from time import time
import concurrent.futures as conc
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
# LXC NO SOPORTA HILOS, CREA CADA CONTENEDOR SECUENCIALMENTE !!!!
def catch_foreach_thread(logger:Logger=None):
    """Ejecuta una funcion tantas veces como argumentos no opcionales
    se hayan pasado a la funcion y maneja las excepciones que puedan 
    surgir durante la ejecucion. Utiliza un hilo por cada ejecucion.
    Hay que tener cuidado de que las funciones que se pasen, no 
    compartan el acceso a variables comunes o que estan esten 
    bloqueadas con candado mientras se modifica su valor. Podrian 
    saltar errores raros (por ejemplo en pickle si se accede a la vez
    a un fichero podria saltar -> ERROR:Ran out of input. Tambien 
    tiene la opcion de ejecutar de forma no concurrente """
    def _catch_foreach(func):
        def catch_concurrently(*args, **optionals):
            successful = []; threads = {}
            with conc.ThreadPoolExecutor() as executor:
                for a in args:
                    thread = executor.submit(func, a, **optionals)
                    threads[thread] = a
            for thread in threads:  
                try:
                    thread.result()
                    successful.append(threads[thread])
                except Exception as err:
                    if str(err) == "":
                        pass
                    elif logger == None:
                        print(f"ERROR:{err}")  
                    else:
                        logger.error(err)    
            return successful
        return catch_concurrently
    return _catch_foreach

# -------------------------------------------------------------------- 
def catch_foreach(logger:Logger=None):
    def _catch_foreach(func):
        def catch(*args, **optionals):
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
    