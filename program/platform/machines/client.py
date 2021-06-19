
import logging

from program.controllers import containers
from dependencies.lxc.lxc_classes.container import Container
from program.platform import platform
from dependencies.lxc import lxc
from dependencies.register import register

# --------------------------- CLIENTE -----------------------------
# --------------------------------------------------------------------
# Este fichero se encarga de proporcionar funciones para crear y 
# configurar los objetos de los clientes que se van a utilizar en 
# la plataforma
# --------------------------------------------------------------------

cl_logger = logging.getLogger(__name__)
# Tag e id de registro para la imagen configurada
TAG = "client"
# --------------------------------------------------------------------
def create_client(name, image:str=None) -> Container:
    # Comprobamos que si hace falta configurar una imagen base para
    # el cliente o ya nos han pasado una o se ha creado antes 
    # y esta disponible
    if get_client() is not None:
        err = " Ya existe un contenedor cliente"
        cl_logger.error(err)
        return None
    j = 1
    while name in lxc.lxc_list():
        name = f"cl{j}"
        j += 1
    # Creamos los objetos de lo cliente
    cl = Container(name, image, tag=TAG)
    cl.add_to_network("eth0", with_ip="10.0.1.2")
    if image is None:
        cl.base_image = platform.default_image
        _config_client(cl)
    else:
        successful = containers.init(cl)
        if len(successful) == 0: cl = None
    return cl

def get_client():
    cs = register.load(containers.ID)
    if cs != None:
        for c in cs:
            if c.tag == TAG:
                return c
    return None

# --------------------------------------------------------------------
def _config_client(cl:Container):
    cl_logger.info(" Configurando cliente...")
    # Lanzamos el contenedor e instalamos modulos
    containers.init(cl); containers.start(cl)
    cl_logger.info(" Instalando lynx (puede tardar)...")
    cl.restart() # Para evitar posibles fallos en la instalacion (dpkg)
    try:
        cl.update_apt()
        cl.install("lynx")
        cl_logger.info(" lynx instalado con exito")
    except lxc.LxcError as err:
        err_msg = (" Fallo al instalar lynx, " + 
                            "error de lxc: " + str(err))
        cl_logger.error(err_msg)
        setattr(cl, "config_error", True)
        containers.stop(cl)
    else:
        containers.stop(cl)
        cl_logger.info(" Cliente configurado con exito\n")
    containers.update_containers(cl)

# --------------------------------------------------------------------