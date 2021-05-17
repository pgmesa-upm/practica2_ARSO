# + Integrantes del grupo: 
# -> Pablo García Mesa
# -> Santiago González Gómez
# -> Fernando Fernández Martín

import sys
import logging

import bash.bash_handler as bash
from bash.bash_handler import CmdLineError
from program import program
from program.program import ProgramError
from program.platform import platform
from dependencies.utils.decorators import timer
 
# ------------------- MAIN (INICIO DE EJECUCION) ---------------------
# --------------------------------------------------------------------
# Este es un fichero fachada en el cual se ve de forma global el 
# flujo de ejecucion que sigue el programa sin entrar en detalles
# --------------------------------------------------------------------
# Los criterios de nivel de logger que va a seguir el programa son:
# --> Se usara:
# - logger.warning():
# cuando se necesite informar al usuario de algo importante
# - logger.error():
# cuando alguna accion no se haya podido completar por algun motivo
# - logger.critical():
# cuando un error impida la continuacion de la ejecucion del programa 
# --------------------------------------------------------------------

logging.basicConfig(level=logging.NOTSET)
main_logger = logging.getLogger(__name__)
# --------------------------------------------------------------------
@timer
def main():
    cli = bash.config_cli()
    try:
        # Procesamos la linea de comandos (CmdLineError)
        args_processed = cli.process_cmdline(sys.argv)
        if args_processed == None: return
        # Configuramos la cantidad de info que se va a mostrar
        _config_verbosity(args_processed["flags"])
        main_logger.info(" Programa iniciado")
        # Realizamos unas comprobaciones previas (ProgramError)
        program.check_dependencies()
        program.check_platform_updates()
        # Ejecutamos la orden
        main_logger.debug(f" Ejecutando la orden {args_processed}")
        bash.execute(args_processed)
        # Actualizamos la plataforma
        platform.update_conexions()
    # Manejamos los errores que puedan surgir 
    except CmdLineError as clErr:
        main_logger.error(f" {clErr}")
    except KeyboardInterrupt:
        main_logger.warning(" Programa interrumpido")
    except ProgramError as err:
        main_logger.critical(err)
    except Exception as err:
        err_msg = " Error inesperado en el programa (no controlado)"
        main_logger.critical(err_msg)
        answer = input("¿Obtener traza completa?(y/n): ")
        if answer.lower() == "y":
            main_logger.exception(err)
    else:
        main_logger.info(" Programa finalizado")
        
# --------------------------------------------------------------------
def _config_verbosity(flags:list):
    """Configura el nivel de verbosidad del programa (nivel de los
    logger de los diferentes ficheros que conforman el programa) en
    funcion de los flags que haya pasado el usuario en la linea de 
    comandos

    Args:
        flags (list): Flags que se han pasado en la linea de comandos
    """
    if "-d" in flags:
        logLvl = logging.DEBUG
    elif "-w" in flags:
        logLvl = logging.WARNING
    elif "-q" in flags:
        logLvl = logging.ERROR
    else:
        logLvl = logging.INFO
    root_logger = logging.getLogger()
    root_logger.setLevel(logLvl) 

# --------------------------------------------------------------------
if __name__ == "__main__":
    main()
# --------------------------------------------------------------------
