import logging

from dependencies.lxc.lxc_classes.container import Container
from program.platform import platform
from dependencies.lxc import lxc
from dependencies.register import register

# --------------------------- SERVIDORES -----------------------------
# --------------------------------------------------------------------
# Este fichero se encarga de proporcionar funciones para crear y 
# configurar los objetos de los clientes que se van a utilizar en 
# la plataforma
# --------------------------------------------------------------------

cl_logger = logging.getLogger(__name__)
# Tag e id de registro para la imagen configurada
TAG = "client"; IMG_ID = "cl_image"
# --------------------------------------------------------------------
def get_client(name="cl",image:str=None) -> Container:
    # Comprobamos que si hace falta configurar una imagen base para
    # el cliente o ya nos han pasado una o se ha creado antes 
    # y esta disponible
    j = 1
    while name in lxc.lxc_list():
        name = f"cl{j}"
        j += 1
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
    cl.add_to_network("eth0", with_ip="10.0.1.2")
    return cl

# --------------------------------------------------------------------
def _config_image() -> str:
    cl_logger.info(" Creando la imagen base de clientes...")
    # Vemos que no haya un contenedor con ese nombre ya
    name = "clconfig"
    j = 1
    while name in lxc.lxc_list():
        name = f"clconfig{j}"
        j += 1
    msg = (f" Contenedor usado para crear imagen " + 
          f"de clientes -> '{name}'")
    cl_logger.debug(msg)
    cl = Container(name, platform.default_image)
    # Lanzamos el contenedor e instalamos modulos
    cl_logger.info(f" Lanzando '{name}'...")
    cl.init(); cl.start()
    cl_logger.info(" Instalando lynx (puede tardar)...")
    try:
        cl.update_apt()
        cl.install("lynx")
        cl_logger.info(" lynx instalado con exito")
    except lxc.LxcError as err:
        err_msg = (" Fallo al instalar lynx, " + 
                            "error de lxc: " + str(err))
        cl_logger.error(err_msg)
        return platform.default_image
    # Vemos que no existe una imagen con el alias que vamos a usar
    alias = "lynx_client"
    k = 1
    images = lxc.lxc_image_list()
    aliases = list(map(lambda f: images[f]["ALIAS"], images))  
    while alias in aliases:
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
    images = lxc.lxc_image_list()
    fingerprint = ""
    for f, info in images.items():
        if info["ALIAS"] == alias:
            fingerprint = f
    image_info = {"alias": alias, "fingerprint": fingerprint}
    register.add(IMG_ID, image_info)
    return alias
# --------------------------------------------------------------------