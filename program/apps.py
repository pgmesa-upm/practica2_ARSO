
import os
import logging
from contextlib import suppress
from os import defpath, path

from program.controllers import containers
from dependencies.register import register
from dependencies.lxc import lxc
from program.platform.machines import servers
from dependencies.process import process
from dependencies.utils.tools import concat_array

app_logger = logging.getLogger(__name__)
# Path relativo (en el programa) al repositorio de aplicaciones
apps_repo_path = "program/resources/apps/"
# --------------------------------------------------------------------
def get_appnames() -> list:
    return os.listdir(apps_repo_path)

def get_defaultapp() -> str:
    default = os.listdir(apps_repo_path+"default")[0]
    return default

def list_apps():
    default = get_defaultapp()
    apps = get_appnames()
    for i, app in enumerate(apps):
        if app == "default":
            apps[i] = app + f"({default})"
    print(" + Apps Repository:" )
    print("     --> ",concat_array(apps,separator=" -- "))
    

# --------------------------------------------------------------------   
def add_app(path:str, name:str=None):
    # obtenemos el nombre de la carpeta original
    parts = path.split("/")
    last = parts[len(parts) - 1]
    if last == "":
        last = parts[len(parts) - 2]
    # Por si es un fichero en vez de una carpeta
    if "." in last:
        file_name = last
        last = last.split(".")[0]
    old_dir_name = last
    # Comprobamos que la ruta existe
    if not os.path.exists(path):
        app_logger.error(f" La ruta absoluta {path} no existe")
        return
    # Creando nueva carpeta
    if name is None:
        name = old_dir_name
    # Comprobamos que no existe una aplicacion con el mismo nombre
    if name in get_appnames():
        err_msg = f" EL nombre '{name}' ya existe en el repositorio"
        app_logger.error(err_msg)
        return
    app_path = apps_repo_path + name + "/"
    app_logger.info(f" Añadiendo app con el nombre '{name}''...")
    process.run(["mkdir", app_path])
    if os.path.isfile(path):
        process.run(["mkdir", app_path+"/ROOT"])
        app_path += "ROOT/"
        old_dir_name = "ROOT"
    try:
        process.shell(f"cp -r {path} {app_path}")
        # Cambiamos su nombre a ROOT para que los server tomcat lo
        # reconozcan al incluirlos en la carpeta webapps
        if old_dir_name != "ROOT":
            process.run(
                ["mv", app_path + old_dir_name, app_path + "ROOT"]
            )
        if os.path.isfile(path) and file_name != "index.html":
            process.run(
                ["mv", app_path + file_name, app_path + "index.html"]
            )
        app_logger.info(f" App '{name}' añadida con exito")
    except process.ProcessErr as err:
        app_logger.error(err)
        process.run(["rm", "-rf", app_path])

def use_app(app_name:str):
    if app_name in get_appnames():
        msg = (f" Actualizando app '{app_name} en servidores...")
        if app_name == "default":
            def_name = get_defaultapp()
            msg = (f" Actualizando app '{app_name}'({def_name}) " +
                        "en servidores...")
            app_name +=  f"/{def_name}"
        app_logger.info(msg)
        change_app(apps_repo_path+app_name+"/ROOT", app_name)
    else:
        err = (f" La aplicacion '{app_name}' no existe en el " + 
                    "repositorio local de aplicaciones")
        app_logger.error(err)

def set_default(app_name:str):
    if app_name in get_appnames():
        def_dir = apps_repo_path+"default"
        old_default = os.listdir(def_dir)
        for d in old_default:
            process.shell(f"cp -r {def_dir}/{d} {apps_repo_path}")
            process.shell(f"rm -rf {def_dir}/{d}")
        process.shell(
            f"mv {apps_repo_path+app_name} {apps_repo_path}/default"
        )
        msg = f" '{app_name}' actualizada como default"
        app_logger.info(msg)
    else:
        err = (f" La aplicacion '{app_name}' no existe en el " + 
                    "repositorio local de aplicaciones")
        app_logger.error(err)

def remove_app(app_name:str):
    if app_name in get_appnames():
        if app_name == "default":
            err = " No se puede eliminar la app por defecto"
            app_logger.error(err)
            return
        process.shell(f"rm -rf {apps_repo_path+app_name}")
        msg = f" Aplicacion '{app_name}' eliminada con exito"
        app_logger.info(msg)
    else:
        err = (f" La aplicacion '{app_name}' no existe en el " + 
                    "repositorio local de aplicaciones")
        app_logger.error(err)

def clear_repository():
    for app_name in get_appnames():
        if app_name == "default":
            continue
        process.shell(f"rm -rf {apps_repo_path+app_name}")
        app_logger.info(f" App '{app_name}' eliminada")
        
# --------------------------------------------------------------------
def mark_htmlindexes(undo=False):
    # Para modificar el index.html de la aplicacion de cada servidor
    # y ver quien es quien. Replace elimina el index.html que haya
    # en el contenedor
    cs = register.load(containers.ID)
    if cs is None:
        app_logger.error(" No hay contenedores creados")
        return
    servs = list(filter(lambda c: c.tag == servers.TAG,cs))
    if len(servs) == 0:
        app_logger.error(" No hay servidores en funcionamiento")
        return
    word1 = "Marcando"
    if undo:
        word1 = "Desmarcando"
    app_logger.info(f" {word1} servidores...")
    index_dir = "/var/lib/tomcat8/webapps/ROOT/"
    index_path = index_dir+"index.html"
    for s in servs:
        if s.state != "RUNNING":
            app_logger.error(f" El servidor {s.name} no esta arrancado")
            continue
        if s.marked and not undo: 
            app_logger.error(f" El servidor {s.name} ya esta marcado")
            continue
        if not s.marked and undo:
            app_logger.error(f" El servidor {s.name} no esta marcado")
            continue
        app_logger.info(f" {word1} servidor '{s.name}'")
        pulled_file = "index.html"
        try:  
            s.pull(index_path, pulled_file)
        except lxc.LxcError as err:
            err_msg = (f" Error al descargar el index.html " + 
                                f"del contenedor '{s.name}':" + str(err))
            app_logger.error(err_msg)
            return
        with open(pulled_file, "r") as file:
            index = file.read()
        old = "<html>"
        new = f"<html><h1> Servidor {s.name} </h1>"
        if undo:
            old = new
            new = "<html>"
        configured_index = index.replace(old, new)
        with open(pulled_file, "w") as f:
            f.write(configured_index)
        try:  
            s.push(pulled_file, index_dir)
        except lxc.LxcError as err:
            err_msg = (f" Error al enviar el index.html marcado" + 
                                f"al contenedor '{s.name}':" + str(err))
            app_logger.error(err_msg)
            return
        if undo:
            s.marked = False
        else:
            s.marked = True
        word2 = word1.lower().replace("n", "")
        app_logger.info(f" Servidor '{s.name}' {word2}")
        os.remove("index.html")
    register.update(containers.ID, cs)

def change_app(app_path, name):
    cs = register.load(containers.ID)
    if cs is None:
        app_logger.error(" No hay contenedores creados")
        return
    servs = list(filter(lambda c: c.tag == servers.TAG,cs))
    if len(servs) == 0:
        app_logger.error(" No hay servidores en funcionamiento")
        return
    webapps_dir = "/var/lib/tomcat8/webapps/"
    root_dir = "/var/lib/tomcat8/webapps/ROOT"
    for s in servs:
        if s.state != "RUNNING":
            app_logger.error(f" El servidor {s.name} no esta arrancado")
            continue
        app_logger.info(f" Actualizando aplicacion de servidor '{s.name}'")
        try: 
            # Eliminamos la aplicacion anterior
            s.execute(["rm", "-rf", root_dir])
        except lxc.LxcError as err:
            err_msg = (f" Error al eliminar la aplicacion anterior: {err}")
            app_logger.error(err_msg)
            return
        try:
            s.push(app_path, webapps_dir)
        except lxc.LxcError as err:
            err_msg = (f" Error al añadir la aplicacion: {err}")
            app_logger.error(err_msg)
            return
        msg = (f" Actualizacion de aplicacion de servidor '{s.name}' " + 
                    "realizada con exito")
        s.app = name
        s.marked = False
        register.update(containers.ID, cs)
        app_logger.info(msg)