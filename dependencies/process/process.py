import subprocess

class ProcessErr(Exception):
    pass

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
    try:
        process = subprocess.run(cmd, **options)
    except Exception as err:
        err_msg = f"El comando introducido no es valido: {err}"
        raise ProcessErr(err_msg)
    outcome = process.returncode
    if outcome != 0:
        err_msg = f" Fallo al ejecutar el comando {cmd}"
        if stderr:
            err = process.stderr.decode()[:-1]
            err_msg += f"\nMensaje de error de lxc: -> {err}"
        elif stdout:
            err_msg = process.stdout.decode()
        raise ProcessErr(err_msg)
    if stdout:
        return process.stdout.decode()

def shell(order:str, stdout=True, stderr=True) -> str:
    # Funcion para evitar problemas con la virgulilla y otros
    # metacaracteres de la shell
    options = {}
    if stdout:
        options["stdout"] = subprocess.PIPE
    options["stderr"] = subprocess.PIPE
    try:
        process = subprocess.run(order, **options, shell=True)
    except Exception as err:
        err_msg = f"El comando introducido no es valido: {err}"
        raise ProcessErr(err_msg)
    outcome = process.returncode
    if outcome != 0:
        err_msg = f" Fallo al ejecutar el comando {order}"
        if stderr:
            err = process.stderr.decode()[:-1]
            err_msg += f"\nMensaje de error de lxc: -> {err}"
        elif stdout:
            err_msg = process.stdout.decode()
        raise ProcessErr(err_msg)
    if stdout:
        return process.stdout.decode()
    