
import logging
from os import remove

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
TAG = "data base"
# Puerto en que se van a ejecutar
db_ip = "10.0.0.20"
# --------------------------------------------------------------------
def create_database(image:str=None, start=False) -> Container:
    # Comprobamos que si hace falta configurar una imagen base para
    # la base de datos o ya nos han pasado una o se ha creado antes 
    # y esta disponible
    name = "db"
    j = 1
    while name in lxc.lxc_list():
        name = f"db{j}"
        j += 1
    # Creamos el objeto de la base de datos
    db = Container(name, image, tag=TAG)
    if image is None:
        db.base_image = platform.default_image
        outcome = _config_database(db, start=start)
        if outcome == -1:
            return
    db.add_to_network("eth0", with_ip=db_ip)
    containers.update_cs_and_notify(db)

# --------------------------------------------------------------------
def _config_database(db:Container, start=False) -> str:
    db_logger.info(" Configurando base de datos...")
    # Lanzamos el contenedor e instalamos modulos
    db_logger.info(f" Lanzando '{db}'...")
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
        db_logger.error(f" Eliminando '{db}'")
        db.stop(); db.delete()
        return -1
    # Configuramos el mongo file
    _config_mongofile(db)
    # Paramos el contenedor
    if not start:
        db.stop()
    db_logger.info(" Base de datos configurada\n")

def _config_mongofile(db:Container):
    msg = " Configurando el fichero mongodb de la base de datos..."
    db_logger.info(msg)
    basicfile_path = "program/resources/config_files/base_mongodb.conf"
    with open(basicfile_path, "r") as file:
        base_file = file.read()
    old = "bind_ip = 127.0.0.1"
    new = f"bind_ip = 127.0.0.1,{db_ip}"
    configured_file = base_file.replace(old, new)
    try:
        path = "/etc/"; file_name = "mongodb.conf"
        with open(file_name, "w") as file:
            file.write(configured_file)
        db.push(file_name, path)
        db_logger.info(" Fichero configurado con exito")
    except lxc.LxcError as err:
        err_msg = f" Fallo al configurar el fichero de mongodb: {err}" 
        db_logger.error(err_msg)
    remove(file_name)
# --------------------------------------------------------------------    