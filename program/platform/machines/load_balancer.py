
import subprocess
import logging
from os import remove

from program import program
from program.controllers import containers
import dependencies.register.register as register
from dependencies.lxc_classes.container import Container
from dependencies.utils.tools import objectlist_as_dict
from dependencies.utils.lxc_functions import checkin_lxclist

# ---------------------- BALANCEADOR DE CARGA ------------------------
# --------------------------------------------------------------------
# Este fichero se encarga de proporcionar funciones para crear y 
# configurar el objeto del balanceador de carga que se va a utilizar
# en la plataforma
# --------------------------------------------------------------------

lb_logger = logging.getLogger(__name__)
# Tag e id de registro para la imagen configurada
TAG = "load balancer"; IMG_ID = "lb_image" 
# Imagen por defecto sobre la que se va a realizar la configuracion
default_image = "ubuntu:18.04"
# --------------------------------------------------------------------
def get_lb(image:str=None) -> Container:
    """Devuelve el objeto del LB configurado

    Args:
        image (str, optional): imagen del contenedor a usar.
            Si es None, crea una imagen propia para el balanceador
            configurada y funcional (permite actuar al contenedor 
            como un balanceador de trafico)

    Returns:
        Container: objeto del balanceador de carga configurado
    """
    if image == None:
        img_saved = register.load(IMG_ID)
        if img_saved is None:
            image = _configure_image()
        else:
            # Comprobamos que la imagen no se haya borrado en lxc
            fgp = img_saved["fingerprint"]
            msg = f" Imagen anterior guardada del balanceador '{fgp}'"
            lb_logger.debug(msg)
            if checkin_lxclist(["lxc", "image", "list"], 1, fgp):
                # Vemos el alias de la imagen por si se ha modificado 
                process = subprocess.run(
                    ["lxc","image","list"],
                    stdout=subprocess.PIPE
                )
                lista = process.stdout.decode()
                images = program.lxclist_as_dict(lista)
                headers = list(images.keys())
                alias = ""
                for i, fg in enumerate(images[headers[1]]):
                    if fg == fgp:
                        alias = images[headers[0]][i]
                        break
                image_info = {"alias": alias, "fingerprint": fgp}
                register.update(IMG_ID, image_info, override=True)
                image = alias
                if alias == "": image = fgp
                msg = f" Alias actual de la imagen del lb -> '{alias}'"
                lb_logger.debug(msg)
            else:
                # como se ha eliminado creamos otra nueva
                msg = (f" Imagen del balanceador se ha borrado" + 
                        "desde fuera del programa")
                lb_logger.debug(msg)
                register.remove(IMG_ID)
                image = _configure_image()
    lb_logger.debug(f" Creando balanceador con imagen '{image}'")
    lb = Container("lb", image, tag=TAG)
    lb.add_to_network("eth0", "10.0.0.10")
    lb.add_to_network("eth1", "10.0.1.10")
    return lb

# --------------------------------------------------------------------
def _configure_image() -> str:
    """Crea una imagen para el balanceador de carga completamente
    configurada y funcional a partir de la default_image

    Returns:
        str: alias de la imagen creada
    """
    lb_logger.info(" Creando la imagen base del balanceador...")
    # Vemos que no haya un contenedor con ese nombre ya
    name = "lbconfig"
    j = 1
    while checkin_lxclist(["lxc", "list"], 0, name):
        name = f"lbconfig{j}"
        j += 1
    msg = f" Contenedor usado para crear la imagen del lb -> '{name}'"
    lb_logger.debug(msg)
    lb_c = Container(name, default_image)
    # Lanzamos el contenedor e instalamos haproxy
    lb_c.init(); lb_c.start()
    lb_logger.info(" Instalando haproxy (puede tardar)...")
    lb_c.wait_for_startup()
    process = subprocess.run(
        ["lxc","exec",name,"--","apt","update"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    process = subprocess.run(
        ["lxc","exec",name,"--","apt","install","-y","haproxy"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    if process.returncode == 0:
        lb_logger.info(" Haproxy instalado con exito")
    else:
        lb_logger.error(" Fallo al instalar haproxy")
    # Configuramos el netfile
    lb_c.add_to_network("eth0", "10.0.0.10")
    lb_c.add_to_network("eth1", "10.0.1.10")
    containers.configure_netfile(lb_c)
    # Vemos que no existe una imagen con el alias que vamos a usar
    alias = "haproxy_lb"
    k = 1
    while checkin_lxclist(["lxc", "image", "list"], 0, alias):
        alias = f"haproxy_lb{k}"
        k += 1
    # Una vez el alias es valido publicamos la imagen
    msg = f" Publicando la imagen del lb con alias '{alias}'..."
    lb_logger.info(msg)
    lb_c.stop()
    process = subprocess.run(
        ["lxc", "publish", name, "--alias", alias],
        stdout=subprocess.PIPE
    )
    lb_logger.info(" Imagen base del balanceador creada\n")
    # Eliminamos el contenedor
    lb_c.delete()
    # Guardamos la imagen en el registro y la devolvemos
    process = subprocess.run(
        ["lxc","image","list"],
        stdout=subprocess.PIPE
    )
    images = program.lxclist_as_dict(process.stdout.decode())
    headers = list(images.keys())
    fingerprint = ""
    for i, al in enumerate(images[headers[0]]):
        if al == alias:
            fingerprint = images[headers[1]][i]
    image_info = {"alias": alias, "fingerprint": fingerprint}
    register.add(IMG_ID, image_info)
    return alias

# --------------------------------------------------------------------
def update_haproxycfg():
    return
    config = (
        "\nfrontend firstbalance" +
        "        bind *:80" +
        "        option forwardfor" +
        "        default_backend webservers" +
        "\nbackend webservers" +
        "        balance roundrobin" +
        "        server webserver1 s1:8080" +
        "        server webserver2 s2:8080" +
        "        server webserver3 s3:8080" +
        "        server webserver1 s1:8080 check" +
        "        server webserver2 s2:8080 check" +
        "        server webserver3 s3:8080 check" +
        "        option httpchk"
    )
    path = None # Donde se encuentre el fichero haproxy.cfg
    subprocess.run("lxc", "exec", "lb", "--", config, ">>", path)
# --------------------------------------------------------------------