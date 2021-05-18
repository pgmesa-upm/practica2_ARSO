
import logging

from program.controllers import containers
from dependencies.register import register
from dependencies.lxc.lxc_classes.container import Container
from dependencies.utils.tools import objectlist_as_dict
from dependencies.lxc import lxc
from program.platform import platform
# --------------------------- SERVIDORES -----------------------------
# --------------------------------------------------------------------
# Este fichero se encarga de proporcionar funciones para crear y 
# configurar el objeto de la base de datos que se va a utilizar en 
# la plataforma
# --------------------------------------------------------------------

db_logger = logging.getLogger(__name__)
# Tag e id de registro para la imagen configurada
TAG = "data base"; IMG_ID = "db_image"
# Puerto en que se van a ejecutar
PORT = 8080
# --------------------------------------------------------------------
def get_database(image:str=None) -> Container:
    # Comprobamos que si hace falta configurar una imagen base para
    # los servidores o ya nos han pasado una o se ha creado antes 
    # y esta disponible 
    name = "db"
    j = 1
    while name in lxc.lxc_list():
        name = f"db{j}"
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
    db = Container(name, image, tag=TAG)
    db.add_to_network("eth0", with_ip="10.0.0.20")
    return db

def _config_image() -> str:
    db_logger.info(" Creando la imagen base de la base de datos...")
    # Vemos que no haya un contenedor con ese nombre ya
    name = "dbconfig"
    j = 1
    while name in lxc.lxc_list():
        name = f"dbconfig{j}"
        j += 1
    msg = (f" Contenedor usado para crear imagen " + 
          f"de la base de datos -> '{name}'")
    db_logger.debug(msg)
    db = Container(name, platform.default_image)
    # Lanzamos el contenedor e instalamos modulos
    db_logger.info(f" Lanzando '{name}'...")
    db.init(); db.start()
    db_logger.info(" Instalando mongodb (puede tardar)...")
    try:
        db.update_apt()
        db.install("mongodb")
        db_logger.info(" mongodb instalado con exito")
    except lxc.LxcError as err:
        err_msg = (" Fallo al instalar mongodb, " + 
                        "error de lxc: " + str(err))
        db_logger.error(err_msg)
        return platform.default_image
    # Vemos que no existe una imagen con el alias que vamos a usar
    alias = "mongo_db"
    k = 1
    images = lxc.lxc_image_list()
    aliases = list(map(lambda f: images[f]["ALIAS"], images))  
    while alias in aliases:
        alias = f"mongo_db{k}"
        k += 1
    # Una vez el alias es valido publicamos la imagen
    msg = (f" Publicando imagen base de la base de datos " + 
           f"con alias '{alias}'...")
    db_logger.info(msg)
    db.stop(); db.publish(alias=alias)
    db_logger.info(" Imagen base de servidores creada\n")
    # Eliminamos el contenedor
    db.delete()
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

def _config_mongofile(c:Container):
    pass