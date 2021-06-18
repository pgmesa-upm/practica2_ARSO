
import os
import logging

from program.controllers import containers
from dependencies.register import register
from program.platform.machines import servers
from dependencies.process import process
from dependencies.utils.tools import concat_array

app_logger = logging.getLogger(__name__)
# Path relativo (en el programa) al repositorio de aplicaciones
apps_repo_path = "program/resources/apps"
apps_default_path = f"{apps_repo_path}/default"
# --------------------------------------------------------------------
def get_appnames() -> list:
    dirs = os.listdir(apps_repo_path)
    apps = []
    for d in dirs: 
        if d == "default":
            default = get_defaultapp()
            if default is not None:
                apps.append(default)
            continue
        apps.append(d)
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
    ordered_apps.append(f"default({default})")
    if default in apps:
        apps.remove(default)
    ordered_apps += apps
    print(" + Apps Repository:" )
    msg = concat_array(ordered_apps,separator=" -- ")
    if default is None and len(apps) == 0:
        msg = "El repositorio de aplicaciones esta vacio"
    print("     --> ", msg)
    
# --------------------------------------------------------------------  
def add_app(path:str, with_name:str=None):
    if path is None: return
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
        if with_name is not None: name = with_name
        app_logger.info(f" Añadiendo app con el nombre '{name}'...")
        if name in get_appnames():
            msg = f" La aplicacion {name} ya existe en el repositorio"
            app_logger.error(msg)
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
        if with_name is not None: name = with_name
        app_logger.info(f" Añadiendo app con el nombre '{name}'...")
        app_path = f"{apps_repo_path}/{name}"
        if name in get_appnames():
            app_logger.error(f" La aplicacion {name} ya existe")
            return
        process.run(["mkdir", app_path])
        process.run(["mkdir", f"{app_path}/ROOT"]) 
        process.shell(f"cp -r {path} {app_path}/ROOT/index.html")
    app_logger.info(f" App '{name}' añadida con exito")
        
def use_app(app_name:str, *servs):
    if app_name in get_appnames() or app_name == "default":
        msg = (f" Actualizando app '{app_name}' en servidores...")
        default = get_defaultapp()
        if app_name == default or app_name == "default":
            app_name = get_defaultapp()
            if app_name is None:
                msg = (f" No existe una aplicacion definida como " +
                        "default")
                app_logger.error(msg)
                return
            msg = (f" Actualizando app '{app_name}' " +
                   f"en servidores '{concat_array(servs)}'...")
            app_logger.info(msg)
            root_path = f"{apps_default_path}/{app_name}/ROOT"
        else:
            app_logger.info(msg)
            root_path = f"{apps_repo_path}/{app_name}/ROOT"
        cs = register.load(containers.ID)
        if cs is None:
            app_logger.error(" No hay contenedores creados")
            return
        existing_servs = list(filter(lambda c: c.tag == servers.TAG, cs))
        namesof_existing_servs = list(map(lambda s: s.name, existing_servs))
        if len(existing_servs) == 0:
            app_logger.error(" No hay servidores en funcionamiento")
            return
        if len(servs) == 0:
            servs = existing_servs
        else:
            for s in servs: 
                if s not in namesof_existing_servs:
                    msg = f" No existe el servidor '{s}' en el programa"
                    app_logger.error(msg)
            servs = list(filter(
                lambda s: s.name in servs, existing_servs
            )) 
        for s in servs:
            servers.change_app(s, root_path, app_name)
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
        
def unset_default():
    if get_defaultapp() is None:
        app_logger.error(f" Default ya esta vacio")
        return
    old_default = os.listdir(apps_default_path)
    for d in old_default:
        process.shell(
            f"cp -r {apps_default_path}/{d} {apps_repo_path}/"
        )
        process.shell(
            f"rm -rf {apps_default_path}/{d}"
        )
        msg = f" La app '{d}' ha dejado de ser la app por defecto"
        app_logger.info(msg)
    msg = f" Ya no hay una aplicacion establecida por defecto"
    app_logger.info(msg)
 
def remove_app(app_name:str):
    base_path = apps_repo_path
    if app_name == "default" or app_name == get_defaultapp(): 
        app_name = get_defaultapp()
        base_path = apps_default_path
    if app_name in get_appnames():
        process.shell(f"rm -rf {base_path}/{app_name}")
        msg = f" Aplicacion '{app_name}' eliminada con exito"
        app_logger.info(msg)
    else:
        err = (f" La aplicacion '{app_name}' no existe en el " + 
                    "repositorio local de aplicaciones")
        app_logger.error(err)

def clear_repository(skip:list=[]):
    apps = get_appnames()
    if len(apps) == 0:
        app_logger.error(" El repositorio de aplicaciones esta vacio")
        return
    removed = False
    for app_name in apps:
        if app_name in skip:
            continue
        base_path = apps_repo_path
        if app_name == "default" or app_name == get_defaultapp(): 
            app_name = get_defaultapp()
            base_path = apps_default_path
        process.shell(f"rm -rf {base_path}/{app_name}")
        removed = True
        if app_name == get_defaultapp():
            app_logger.info(f" App default '{app_name}' eliminada")
        else:
            app_logger.info(f" App '{app_name}' eliminada")
    if not removed:
        app_logger.warning(" No se han seleccionado apps para eliminar")
        
# --------------------------------------------------------------------
