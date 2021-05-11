import logging

from dependencies.lxc_classes.container import Container

# --------------------------- SERVIDORES -----------------------------
# --------------------------------------------------------------------
# Este fichero se encarga de proporcionar funciones para crear y 
# configurar los objetos de los clientes que se van a utilizar en 
# la plataforma
# --------------------------------------------------------------------

cl_logger = logging.getLogger(__name__)
# Tag e id de registro para la imagen configurada
TAG = "client"; IMG_ID = "cl_image"
# Imagen por defecto sobre la que se va a realizar la configuracion
default_image = "ubuntu:18.04"
# --------------------------------------------------------------------
def get_client(image:str=None) -> Container:
    if image is None:
        image = default_image
    cl = Container("cl", image, tag=TAG)
    cl.add_to_network("eth0", "10.0.1.2")
    return cl