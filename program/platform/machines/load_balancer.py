
import logging
from os import remove
from pickle import FALSE
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
PORT = 80
# --------------------------------------------------------------------
def create_lb(image:str=None, balance=None) -> Container:
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
    setattr(lb, "port", PORT)
    setattr(lb, "algorithm", balance)
    if image is None:
        lb.base_image = platform.default_image
        _config_loadbalancer(lb)
    else:
        successful = containers.init(lb)
        if len(successful) == 0: lb = None
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
        update_haproxycfg()
        containers.stop(lb)
        msg = " Balanceador de carga configurado con exito\n"
        lb_logger.info(msg)
    containers.update_cs_without_notify(lb) 

# --------------------------------------------------------------------
def update_haproxycfg():
    lb = get_lb()
    if lb is None: return
    # Miramos si el lb esta arrancado para actualizar (si no lo 
    # haremos la proxima vez que arranque) y si lo esta esperamos
    # a que termine el startup
    if lb.state != "RUNNING":
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
    try:
        path = "/etc/haproxy/"; file_name = "haproxy.cfg"
        with open(file_name, "w") as file:
            file.write(configured_file)
        lb.push(file_name, path)
        lb.execute(["haproxy", "-f", path+file_name, "-c"])
        lb.execute(["service","haproxy","restart"])
        lb_logger.info(" Fichero haproxy actualizado con exito")
    except lxc.LxcError as err:
        err_msg = f" Fallo al configurar el fichero haproxy: {err}" 
        lb_logger.error(err_msg)
        lb.algorithm = default_algorithm
        containers.update_cs_without_notify(lb)
        return -1
    remove("haproxy.cfg")
    
# --------------------------------------------------------------------
def change_algorithm(algorithm:str):
    global default_algorithm
    cs = register.load(containers.ID)
    if cs is None: 
        lb_logger.error(" No existen contenedores en la plataforma")
        return
    lb = None
    for c in cs:
        if c.tag == TAG:
            lb = c
            break
    if lb == None:
        err = " No existe un balanceador de carga en la plataforma"
        lb_logger.error(err)
        return
    if lb.state != "RUNNING":
        lb_logger.error(" El balanceador no se encuentra arrancado")
        return
    lb.algorithm = algorithm
    register.update(containers.ID, cs)
    outcome = update_haproxycfg()
    if outcome == -1:
        msg = (" Fallo al cambiar el algoritmo de balanceo, se " + 
                "utilizara el algoritmo por defecto")
        lb_logger.error(msg)
# --------------------------------------------------------------------
    
    