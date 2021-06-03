
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
PORT = 80
# --------------------------------------------------------------------
def get_lb(image:str=None, balance=None) -> Container:
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
    if image is None:
        if platform.is_imageconfig_needed(IMG_ID):
            image = _config_image()
        else:
            image_saved = register.load(IMG_ID)
            alias = image_saved["alias"]
            image = alias
            if alias == "": image = image_saved["fingerprint"]
    if balance is None:
        balance = default_algorithm
    # Creamos el objeto del balanceador
    msg = (f" Creando balanceador con imagen '{image}' " + 
           f"y algoritmo de balanceo '{balance}'")
    lb_logger.debug(msg)
    name = "lb"
    j = 1
    while name in lxc.lxc_list():
        name = f"lb{j}"
        j += 1
    lb = Container(name, image, tag=TAG)
    lb.add_to_network("eth0", with_ip="10.0.0.10")
    lb.add_to_network("eth1", with_ip="10.0.1.10")
    setattr(lb, "port", PORT)
    setattr(lb, "algorithm", balance)
    return lb

# --------------------------------------------------------------------
def _config_image() -> str:
    """Crea una imagen para el balanceador de carga completamente
    configurada y funcional a partir de la default_image

    Returns:
        str: alias de la imagen creada
    """
    lb_logger.info(" Creando la imagen base del balanceador...")
    # Vemos que no haya un contenedor con ese nombre ya
    name = "lbconfig"
    j = 1
    while name in lxc.lxc_list():
        name = f"lbconfig{j}"
        j += 1
    msg = f" Contenedor usado para crear la imagen del lb -> '{name}'"
    lb_logger.debug(msg)
    lb_c = Container(name, platform.default_image, tag=TAG)
    # Lanzamos el contenedor e instalamos modulos
    lb_logger.info(f" Lanzando '{name}'...")
    lb_c.init(); lb_c.start()
    lb_logger.info(" Instalando haproxy (puede tardar)...")
    try:
        lb_c.update_apt()
        lb_c.install("haproxy")
        lb_c.execute(["service","haproxy","start"])
    except lxc.LxcError as err:
        err_msg = (" Fallo al instalar haproxy, " + 
                            "error de lxc: " + str(err))
        lb_logger.error(err_msg)
        return platform.default_image
    # Configuramos el netfile
    lb_c.add_to_network("eth0")
    lb_c.add_to_network("eth1")
    containers.configure_netfile(lb_c)
    # Configurmaos el haproxy file
    setattr(lb_c, "port", PORT)
    setattr(lb_c, "algorithm", default_algorithm)
    register.add(containers.ID, [lb_c])
    update_haproxycfg()
    register.remove(containers.ID)
    # Vemos que no existe una imagen con el alias que vamos a usar
    alias = "haproxy_lb"
    k = 1
    images = lxc.lxc_image_list()
    aliases = list(map(lambda f: images[f]["ALIAS"], images))  
    while alias in aliases:
        alias = f"haproxy_lb{k}"
        k += 1
    # Una vez el alias es valido publicamos la imagen
    msg = f" Publicando la imagen del lb con alias '{alias}'..."
    lb_logger.info(msg)
    lb_c.stop(); lb_c.publish(alias=alias)
    lb_logger.info(" Imagen base del balanceador creada\n")
    # Eliminamos el contenedor
    lb_c.delete()
    # Guardamos la imagen en el registro y la devolvemos
    images = lxc.lxc_image_list()
    fingerprint = ""
    for f, info in images.items():
        if info["ALIAS"] == alias:
            fingerprint = f
    image_info = {"alias": alias, "fingerprint": fingerprint}
    register.add(IMG_ID, image_info)
    return alias

# --------------------------------------------------------------------
def update_haproxycfg():
    # Miramos si existen contenedores creados
    cs = register.load(containers.ID)
    if cs is None: return
    # Si se ha borrado el balanceador desde fuera del programa o no
    # se encuentra arrancado para actualizar salimos
    lb = None
    for c in cs:
        if c.tag == TAG:
            lb = c
            break
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
        lb.algorithm = default_algorithm
        containers.update_containers(lb)
# --------------------------------------------------------------------
    
    