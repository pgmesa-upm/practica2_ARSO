import logging

from dependencies.lxc.lxc_classes.container import Container
from program.platform import platform
from dependencies.lxc.lxc_functions import (
    checkin_lxclist,
    lxc_image_list,
    process_lxclist
)
import dependencies.register.register as register

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
def get_client(name="cl",image:str=None) -> Container:
    # Comprobamos que si hace falta configurar una imagen base para
    # el cliente o ya nos han pasado una o se ha creado antes 
    # y esta disponible
    if image is None:
        if platform.is_imageconfig_needed(IMG_ID):
            image = _config_image()
        else:
            image_saved = register.load(IMG_ID)
            alias = image_saved["alias"]
            image = alias
            if alias == "": image = image_saved["fingerprint"]
    # Creamos los objetos de lo cliente
    cl = Container(name, image, tag=TAG)
    cl.add_to_network("eth0", "10.0.1.2")
    return cl

# --------------------------------------------------------------------
def _config_image() -> str:
    cl_logger.info(" Creando la imagen base de clientes...")
    # Vemos que no haya un contenedor con ese nombre ya
    name = "clconfig"
    j = 1
    while checkin_lxclist(["lxc", "list"], 0, name):
        name = f"clconfig{j}"
        j += 1
    msg = (f" Contenedor usado para crear imagen " + 
          f"de clientes -> '{name}'")
    cl_logger.debug(msg)
    cl = Container(name, default_image)
    # Lanzamos el contenedor e instalamos modulos
    cl_logger.info(f" Lanzando '{name}'...")
    cl.init(); cl.start()
    cl_logger.info(" Instalando lynx (puede tardar)...")
    cl.update_apt()
    try:
        cl.install("lynx")
        cl_logger.info(" lynx instalado con exito")
    except:
        cl_logger.error(" Fallo al instalar lynx")
        return default_image
    # Vemos que no existe una imagen con el alias que vamos a usar
    alias = "lynx_client"
    k = 1
    while checkin_lxclist(["lxc", "image", "list"], 0, alias):
        alias = f"lynx_client{k}"
        k += 1
    # Una vez el alias es valido publicamos la imagen
    msg = (f" Publicando imagen base de clientes " + 
           f"con alias '{alias}'...")
    cl_logger.info(msg)
    cl.stop(); cl.publish(alias=alias)
    cl_logger.info(" Imagen base de clientes creada\n")
    # Eliminamos el contenedor
    cl.delete()
    # Guardamos la imagen en el registro y la devolvemos 
    # (obtenemos tambien la huella que le ha asignado lxc)
    l = lxc_image_list()
    images = process_lxclist(l)
    headers = list(images.keys())
    fingerprint = ""
    for i, al in enumerate(images[headers[0]]):
        if al == alias:
            fingerprint = images[headers[1]][i]
    image_info = {"alias": alias, "fingerprint": fingerprint}
    register.add(IMG_ID, image_info)
    return alias
# --------------------------------------------------------------------