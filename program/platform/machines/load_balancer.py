
import logging
from os import remove

from dependencies import lxc
from program.controllers import containers
from dependencies.register import register
from dependencies.lxc.lxc_classes.container import Container
from dependencies.lxc import lxc
from program.platform.machines import servers
from program.platform import platform

# ---------------------- BALANCEADOR DE CARGA ------------------------
# --------------------------------------------------------------------
# Este fichero se encarga de proporcionar funciones para crear y 
# configurar el objeto del balanceador de carga que se va a utilizar
# en la plataforma
# --------------------------------------------------------------------

lb_logger = logging.getLogger(__name__)
# Tag e id de registro para la imagen configurada
TAG = "load balancer"; IMG_ID = "lb_image" 
# Algoritmo de balanceo de trafico
default_algorithm = "roundrobin"
# Puerto en el que se va a ejecutar para aceptar conexiones de clientes
# por defecto
default_port = 80
# --------------------------------------------------------------------
def create_lb(image:str=None, balance:str=None, port:int=None) -> Container:
    """Devuelve el objeto del LB configurado

    Args:
        image (str, optional): imagen del contenedor a usar.
            Si es None, crea una imagen propia para el balanceador
            configurada y funcional (permite actuar al contenedor 
            como un balanceador de trafico)

    Returns:
        Container: objeto del balanceador de carga configurado
    """
    # Comprobamos que si hace falta configurar una imagen base para
    # el balanceador o ya se ha creado antes y esta disponible
    j = 1; name = "lb"
    while name in lxc.lxc_list():
        name = f"lb{j}"
        j += 1
    if balance is None:
        balance = default_algorithm
    # Creamos el objeto del balanceador
    msg = (f" Creando balanceador con imagen '{image}' " + 
           f"y algoritmo de balanceo '{balance}'")
    lb_logger.debug(msg)
    lb = Container(name, image, tag=TAG)
    lb.add_to_network("eth0", with_ip="10.0.0.10")
    lb.add_to_network("eth1", with_ip="10.0.1.10")
    if port is None:
        port = default_port
    setattr(lb, "port", port)
    setattr(lb, "algorithm", balance)
    if image is None:
        lb.base_image = platform.default_image
        _config_loadbalancer(lb)
    else:
        successful = containers.init(lb)
        if len(successful) == 0: 
            lb = None
        else:
            lb.start(); update_haproxycfg(lb); lb.stop()
    return lb

def get_lb():
    cs = register.load(containers.ID)
    if cs != None:
        for c in cs:
            if c.tag == TAG:
                return c
    return None
    
# --------------------------------------------------------------------
def _config_loadbalancer(lb:Container):
    """Crea una imagen para el balanceador de carga completamente
    configurada y funcional a partir de la default_image

    Returns:
        str: alias de la imagen creada
    """
    lb_logger.info(" Configurando balanceador de carga...")
    # Lanzamos el contenedor e instalamos modulos
    containers.init(lb); containers.start(lb)
    # Configuramos el netfile
    containers.configure_netfile(lb)
    lb_logger.info(" Instalando haproxy (puede tardar)...")
    lb.restart() # Para evitar posibles fallos en la instalacion (dpkg)
    try:
        lb.update_apt()
        lb.install("haproxy")
        lb.execute(["service","haproxy","start"])
    except lxc.LxcError as err:
        err_msg = (" Fallo al instalar haproxy, " + 
                            "error de lxc: " + str(err))
        lb_logger.error(err_msg)
        setattr(lb, "config_error", True)
        containers.stop(lb)
    else:
        # Configurmaos el haproxy file
        update_haproxycfg(lb)
        containers.stop(lb)
        msg = " Balanceador de carga configurado con exito\n"
        lb_logger.info(msg)
    containers.update_containers(lb) 

# --------------------------------------------------------------------
def update_haproxycfg(lb:Container, reset_on_fail=True):
    # Miramos si el lb esta arrancado para actualizar (si no lo 
    # haremos la proxima vez que arranque) y si lo esta esperamos
    # a que termine el startup
    if lb is None or lb.state != "RUNNING":
        return
    # Actualizamos el fichero
    lb_logger.info(" Actualizando el fichero haproxy del balanceador...")
    lb_logger.info(" Esperando startup del balanceador...")
    lb.wait_for_startup()
    lb_logger.info(" Startup finalizado")
    # Procedemos a configurar el fichero de haproxy
    config = (
         "\n\nfrontend firstbalance\n" +
        f"        bind *:{lb.port}\n" +
         "        option forwardfor\n" +
         "        default_backend webservers\n" +
         "backend webservers\n" +
        f"        balance {lb.algorithm}\n"
    )
    cs = register.load(containers.ID)
    if cs is None:
        servs = []
    else:
        servs = list(filter(
            lambda c: c.tag == servers.TAG and c.state == "RUNNING",
            cs
        ))
    for i, s in enumerate(servs):
        l = f"        server webserver{i+1} {s.name}:{s.port}\n"
        config += l
    for i, s in enumerate(servs):
        l = f"        server webserver{i+1} {s.name}:{s.port} check\n"
        config += l
    config += "        option httpchk"
    lb_logger.debug(config)
    # Leemos la info basica del fichero basic_haproxy.cfg
    basicfile_path = "program/resources/config_files/base_haproxy.cfg"
    with open(basicfile_path, "r") as file:
        base_file = file.read()
    # Juntamos los ficheros
    configured_file = base_file + config
    # Creamos el fichero haproxy.cfg lo enviamos al contenedor y
    # eliminamos el fichero que ya no nos hace falta
    fail = False
    try:
        path = "/etc/haproxy/"; file_name = "haproxy.cfg"
        with open(file_name, "w") as file:
            file.write(configured_file)
        lb.push(file_name, path)
        lb.execute(["haproxy", "-f", path+file_name, "-c"])
        lb.execute(["service","haproxy","restart"])
        lb_logger.info(" Fichero haproxy actualizado con exito")
    except lxc.LxcError as err:
        fail = True
        err_msg = f" Fallo al configurar el fichero haproxy: {err}" 
        lb_logger.error(err_msg)
    remove("haproxy.cfg")
    if fail: 
        if reset_on_fail:
            reset_config()
        return -1
    
# --------------------------------------------------------------------
def change_algorithm(algorithm:str):
    global default_algorithm
    lb:Container = get_lb()
    if lb == None:
        err = " No existe el balanceador de carga en la plataforma"
        lb_logger.error(err)
        return
    if lb.state != "RUNNING":
        lb_logger.error(" El balanceador no se encuentra arrancado")
        return
    lb.algorithm = algorithm
    containers.update_containers(lb)
    outcome = update_haproxycfg(lb, reset_on_fail=False)
    if outcome == -1:
        msg = (" Fallo al cambiar el algoritmo de balanceo, se " + 
        f"utilizara el algoritmo por defecto -> {default_algorithm}")
        lb_logger.error(msg)
        lb.algorithm = default_algorithm
        containers.update_containers(lb)
        update_haproxycfg(lb)
        
# --------------------------------------------------------------------
def change_binded_port(port:int):
    lb:Container = get_lb()
    if lb is None:
        msg = " No existe el balanceador de carga en la plataforma"
        lb_logger.error(msg)
        return 
    if lb.state != "RUNNING":
        lb_logger.error(" El balanceador no se encuentra arrancado")
        return
    msg = (" Actualizando puerto de escucha del balanceador " + 
          f"-> {port} ...")
    lb_logger.info(msg)
    msg = (" Puede que algunos puertos no sean validos o no " + 
            "permitan conexiones")
    lb_logger.warning(msg)
    lb.port = port
    containers.update_containers(lb)
    outcome = update_haproxycfg(lb, reset_on_fail=False)
    if outcome == -1:
        msg = (" Fallo al cambiar el puerto de escucha, se " + 
            f"utilizara el puerto por defecto -> {default_port}")
        lb_logger.error(msg)
        lb.port = default_port
        containers.update_containers(lb)
        update_haproxycfg(lb)
    
# --------------------------------------------------------------------
def reset_config():
    lb:Container = get_lb()
    if lb is None:
        msg = " No existe el balanceador de carga en la plataforma"
        lb_logger.error(msg)
        return 
    if lb.state != "RUNNING":
        lb_logger.error(" El balanceador no se encuentra arrancado")
        return
    msg = (" Reseteando configuracion del balanceador ...")
    lb_logger.info(msg)
    lb.port = default_port
    lb.algorithm = default_algorithm
    containers.update_containers(lb)
    update_haproxycfg(lb)