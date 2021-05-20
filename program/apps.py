
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
apps_repo_path = "program/resources/apps"
apps_default_path = f"{apps_repo_path}/default"
# --------------------------------------------------------------------
def get_appnames() -> list:
    apps = os.listdir(apps_repo_path)
    for i, app in enumerate(apps): 
        if app == "default":
            apps[i] = get_defaultapp()
            break
    return apps

def get_defaultapp() -> str:
    l = os.listdir(apps_default_path)
    if len(l) > 0:
        default = l[0]
    else:
        return None
    return default

def list_apps():
    default = get_defaultapp()
    apps = get_appnames()
    ordered_apps = []
    for i, app in enumerate(apps):
        if app == default:
            ordered_apps.append(f"default({app})")
            apps.pop(i)
            break
    ordered_apps += apps
    print(" + Apps Repository:" )
    print("     --> ",concat_array(ordered_apps,separator=" -- "))
    
# --------------------------------------------------------------------   
def add_app(path:str, name:str=None):
    # Comprobamos que la ruta existe
    if not os.path.exists(path):
        app_logger.error(f" La ruta absoluta '{path}' no existe")
        return
    if os.path.isdir(path):
        if path.endswith("/"): 
            path = path[:-1]
        parts = path.split("/")
        name = parts[len(parts) - 1]
        if " " in name:
            err = (f" Los nombres con espacios en blanco '{name}' " +
                    "no estan permitidos")
            app_logger.error(err)
            return
        app_logger.info(f" Añadiendo app con el nombre '{name}'...")
        if name in get_appnames():
            app_logger.error(f" La aplicacion {name} ya existe")
            return
        if "index.html" not in os.listdir(path):
            if "ROOT" not in os.listdir(path):
                err =  (f"El directorio '{path}' no contiene un " + 
                         "archivo de arranque index.html ni una " +
                         "carpeta raiz 'ROOT'")
                app_logger.error(err)
                return
            elif "index.html" not in os.listdir(f"{path}/ROOT"):
                err =  (f"La carpeta raiz '{path}' no contiene un " + 
                         "archivo de arranque index.html")
                app_logger.error(err)
                return
            else:
                # Copiamos directamente la aplicacion
                process.shell(f"cp -r {path} {apps_repo_path}/")
        else:
            app_path = f"{apps_repo_path}/{name}"
            process.run(["mkdir", app_path])
            process.run(["mkdir", f"{app_path}/ROOT"]) 
            process.shell(f"cp -r {path}/* {app_path}/ROOT/")
    elif os.path.isfile(path):
        parts = path.split("/")
        full_name = parts[len(parts) - 1]
        name = full_name.split(".")[0]
        if " " in name:
            err = (f" Los nombres con espacios en blanco '{name}' " +
                    "no estan permitidos")
            app_logger.error(err)
            return
        app_logger.info(f" Añadiendo app con el nombre '{name}'...")
        app_path = f"{apps_repo_path}/{name}"
        if name in get_appnames():
            app_logger.error(f" La aplicacion {name} ya existe")
            return
        process.run(["mkdir", app_path])
        process.run(["mkdir", f"{app_path}/ROOT"]) 
        process.shell(f"cp -r {path} {app_path}/ROOT/index.html")
    app_logger.info(f" App '{name}' añadida con exito")
        
def use_app(app_name:str):
    if app_name in get_appnames() or app_name == "default":
        msg = (f" Actualizando app '{app_name} en servidores...")
        default = get_defaultapp()
        if app_name == default or app_name == "default":
            app_name = get_defaultapp()
            msg = (f" Actualizando app default({app_name}) " +
                        "en servidores...")
            app_logger.info(msg)
            root_path = f"'{apps_default_path}/{app_name}/ROOT'"
            change_app(root_path, app_name)
        else:
            app_logger.info(msg)
            change_app(f"'{apps_repo_path}/{app_name}/ROOT'", app_name)
    else:
        err = (f" La aplicacion '{app_name}' no existe en el " + 
                    "repositorio local de aplicaciones")
        app_logger.error(err)

def set_default(app_name:str):
    if app_name in get_appnames():
        if app_name == get_defaultapp():
            msg = f" La app '{app_name}' ya se esta usando como default"
            app_logger.error(msg)
            return
        old_default = os.listdir(apps_default_path)
        for d in old_default:
            process.shell(
                f"cp -r {apps_default_path}/{d} {apps_repo_path}/"
            )
            process.shell(
                f"rm -rf {apps_default_path}/{d}"
            )
        process.shell(
            f"mv {apps_repo_path}/{app_name} {apps_default_path}/"
        )
        msg = f" '{app_name}' actualizada como default"
        app_logger.info(msg)
    else:
        err = (f" La app '{app_name}' no existe en el " + 
                    "repositorio local de aplicaciones")
        app_logger.error(err)

def remove_app(app_name:str):
    if app_name in get_appnames():
        if app_name == get_defaultapp():
            err = (" No se puede eliminar la app que se esta " + 
                    "usando como default")
            app_logger.error(err)
            return
        process.shell(f"rm -rf {apps_repo_path}/{app_name}")
        msg = f" Aplicacion '{app_name}' eliminada con exito"
        app_logger.info(msg)
    else:
        err = (f" La aplicacion '{app_name}' no existe en el " + 
                    "repositorio local de aplicaciones")
        app_logger.error(err)

def clear_repository():
    for app_name in get_appnames():
        if app_name == get_defaultapp():
            continue
        process.shell(f"rm -rf {apps_repo_path}/{app_name}")
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
        if s.app == name:
            err = (f" El servidor '{s.name}' ya esta usando la " + 
                   f"aplicacion '{name}'")
            app_logger.error(err)
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