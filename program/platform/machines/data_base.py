
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
    db.add_to_network("eth0", with_ip=db_ip)
    if image is None:
        db.base_image = platform.default_image
        _config_database(db)
    else:
        successful = containers.init(db)
        if len(successful) == 0: 
            db = None
        else:
            db.start(); _config_mongofile(db); db.stop()
    return db

def get_database():
    cs = register.load(containers.ID)
    if cs != None:
        for c in cs:
            if c.tag == TAG:
                return c
    return None

# --------------------------------------------------------------------
def _config_database(db:Container):
    db_logger.info(" Configurando base de datos...")
    # Lanzamos el contenedor e instalamos modulos
    containers.init(db); containers.start(db)
    db_logger.info(" Instalando mongodb (puede tardar)...")
    db.restart() # Para evitar posibles fallos en la instalacion (dpkg)
    try:
        db.update_apt()
        db.install("mongodb")
        db_logger.info(" mongodb instalado con exito")
    except lxc.LxcError as err:
        err_msg = (" Fallo al instalar mongodb, " + 
                        "error de lxc: " + str(err))
        db_logger.error(err_msg)
        setattr(db, "config_error", True)
        containers.stop(db)
    else:
        # Configuramos el mongo file
        _config_mongofile(db)
        containers.stop(db)
        db_logger.info(" Base de datos configurada con exito\n")
    containers.update_containers(db)
    
def _config_mongofile(db:Container):
    if db is None or db.state != "RUNNING":
        return
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