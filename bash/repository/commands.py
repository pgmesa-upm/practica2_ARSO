
from concurrent.futures import thread
from dependencies.lxc.lxc_classes.container import Container
import logging
from pickle import load
import concurrent.futures as conc

from .reused_code import (
    target_containers, get_db_opts, get_cl_opts,
    get_lb_opts, get_servers_opts
)
from program.controllers import bridges, containers
from program.platform.machines import (
    servers, load_balancer, net_devices, client, data_base
)
from program import apps
from program import program
from dependencies.register import register
from dependencies.utils.tools import concat_array
from program.platform import platform

# --------------------- REPOSITORIO DE COMANDOS ----------------------
# --------------------------------------------------------------------
# Aqui se definen todas las funciones asociadas a los comandos que 
# tiene el programa. Estas funciones se pueden comunicar entre si 
# mediante variables opcionales adicionales para reutilizar el codigo
# --------------------------------------------------------------------

cmd_logger = logging.getLogger(__name__)
# --------------------------------------------------------------------
@target_containers(cmd_logger)           
def start(*target_cs, options={}, flags=[]):
    """Arranca los contenedores que se enceuntren en target_cs

    Args:
        options (dict, optional): Opciones del comando arrancar
        flags (list, optional): Flags introducidos en el programa
    """
    # Arrancamos los contenedores validos
    msg = f" Arrancando contenedores '{concat_array(target_cs)}'..."
    cmd_logger.info(msg)
    succesful_cs = containers.start(*target_cs)
    if not "-q" in flags:
        program.list_lxc_containers()
    cs_s = concat_array(succesful_cs)
    msg = (f" Los contenedores '{cs_s}' han sido arrancados \n")
    cmd_logger.info(msg)
    # Si nos lo indican, abrimos las terminales de los contenedores 
    # arrancados
    if "-t" in flags and len(succesful_cs) > 0:
        c_names = list(map(lambda c: c.name, target_cs))
        term(*c_names, flags=flags)
    warn = (" Los servicios de los servidores y/o balanceador puede " +
            "tardar unos cuantos segundos en estar disponibles\n")
    cmd_logger.warning(warn)
    # Cargamos la aplicacion
    if apps.get_defaultapp() is not None:
        servs = []
        for c in succesful_cs:
            if c.tag == servers.TAG and c.app is None:
                servs.append(c.name)
        if len(servs) > 0:
            msg = " Cargando la aplicacion por defecto en servidores..."
            cmd_logger.info(msg) 
            apps.use_app("default", *servs)
            cmd_logger.info(" Distribucion de la aplicacion finalizado\n")
    else:
        warn = (" No hay ninguna aplicacion asignada como default " +
                "para desplegar en los servidores\n")
        cmd_logger.warning(warn)
    if "-m" in flags:
        app(options={"markservs":{"args":[], "options":{}, "flags":[]}})
        
# --------------------------------------------------------------------
@target_containers(cmd_logger) 
def stop(*target_cs, options={}, flags=[]):
    """Detiene los contenedores que se enceuntren en target_cs

    Args:
        options (dict, optional): Opciones del comando parar
        flags (list, optional): Flags introducidos en el programa
    """
    # Paramos los contenedores validos
    msg = f" Deteniendo contenedores '{concat_array(target_cs)}'..."
    cmd_logger.info(msg)
    succesful_cs = containers.stop(*target_cs)
    if not "-q" in flags:
        program.list_lxc_containers()
    cs_s = concat_array(succesful_cs)
    msg = (f" Los contenedores '{cs_s}' han sido detenidos \n")
    cmd_logger.info(msg)
        
# --------------------------------------------------------------------  
@target_containers(cmd_logger)  
def pause(*target_cs, options={}, flags=[]):
    """Pausa los contenedores que se enceuntren en target_cs

    Args:
        options (dict, optional): Opciones del comando pausar
        flags (list, optional): Flags introducidos en el programa
    """
    # Pausamos los contenedores validos
    msg = f" Pausando contenedores '{concat_array(target_cs)}'..."
    cmd_logger.info(msg)
    succesful_cs = containers.pause(*target_cs)
    if not "-q" in flags:
        program.list_lxc_containers()
    cs_s = concat_array(succesful_cs)
    msg = (f" Los contenedores '{cs_s}' han sido pausados \n")
    cmd_logger.info(msg)

# --------------------------------------------------------------------
@target_containers(cmd_logger) 
def remove(*target_cs, options={}, flags=[],
            skip_tags=[load_balancer.TAG, data_base.TAG]): 
    """Elimina los contenedores que se enceuntren en target_cs.
    Por defecto, esta funcion solo elimina los contenedores que 
    sean servidores o clientes

    Args:
        options (dict, optional): Opciones del comando eliminar
        flags (list, optional): Flags introducidos en el programa
        skip_tags (list, optional): Variable que permite que destruir
            se comunique con esta funcion. Por defecto esta funcion 
            no elimina contenedores que sean clientes o balanceadores
    """
    # Miramos que contenedores son validos para eliminar
    if len(skip_tags) > 0:
        valid_cs = []
        for c in target_cs:
            if c.tag in skip_tags:
                msg = (f" El contenedor '{c}' no se puede eliminar " + 
                        "(solo servidores o clientes)")
                cmd_logger.error(msg)  
                continue
            valid_cs.append(c)
        if len(valid_cs) == 0: return
        target_cs = valid_cs
    if not "-y" in flags:
        print("Se eliminaran los contenedores:" +
                    f" '{concat_array(target_cs)}'")
        answer = str(input("¿Estas seguro?(y/n): "))
        if answer.lower() != "y":
            return
    # Eliminamos los existentes que nos hayan indicado
    msg = f" Eliminando contenedores '{concat_array(target_cs)}'..."
    cmd_logger.info(msg)
    succesful_cs = containers.delete(*target_cs)
    # Actualizamos la plataforma
    platform.update_conexions()
    if not "-q" in flags:
        program.list_lxc_containers()
    cs_s = concat_array(succesful_cs)
    msg = (f" Los contenedores '{cs_s}' han sido eliminados \n")
    cmd_logger.info(msg)

# --------------------------------------------------------------------
@target_containers(cmd_logger) 
def term(*target_cs, options={}, flags=[]):
    """Abre la terminal los contenedores que se enceuntren en 
    target_cs

    Args:
        options (dict, optional): Opciones del comando term
        flags (list, optional): Flags introducidos en el programa
    """
    # Arrancamos los contenedores validos
    cs_s = concat_array(target_cs)
    msg = f" Abriendo terminales de contenedores '{cs_s}'..."
    cmd_logger.info(msg)
    succesful_cs = containers.open_terminal(*target_cs)
    cs_s = concat_array(succesful_cs)
    msg = f" Se ha abierto la terminal de los contenedores '{cs_s}'\n"
    cmd_logger.info(msg)
    
    # --------------------------------------------------------------------
def add(num:int, options={}, flags=[], extra_cs=[]):
    """Añade el numero de contenedores especificados a la plataforma
    de servidores. Por defecto solo añade contenedores que sean del
    tipo servidor, pero en extra_cs se pueden especificar contenedores 
    de cualquier tipo que tambien se quiran añadir

    Args:
        numServs (int): Numero de servidores a añadir
        options (dict, optional): Opciones del comando añadir
        flags (list, optional): Flags introducidos en el programa
        extra_cs (list, optional): Variable utilizada para que 'crear' se
            pueda comunicar con esta funcion y tambien cree los 
            clientes y el balanceador, ademas de los servidores
    """
    if not platform.is_deployed():
        msg = (
            " La plataforma de servidores no ha sido desplegada, se " +
            "debe crear una nueva antes de añadir los servidores"
        )
        cmd_logger.error(msg)
        return
    
    existent_cs = register.load(containers.ID)
    if "-cl" in options:
        climage, name = get_cl_opts(options)
        client.create_client(name=name, image=climage)
        return
    elif num > 0:
        if existent_cs != None:
            ex_s = filter(lambda cs: cs.tag == servers.TAG, existent_cs)
            n = len(list(ex_s))
            if n + num > 5: 
                msg = (f" La plataforma no admite mas de 5 servidores. " +
                        f"Existen {n} actualmente, no se " +
                        f"pueden añadir {num} mas")
                cmd_logger.error(msg)
                return
        simage, names = get_servers_opts(options)
        servs = servers.create_servers(num, *names, image=simage)
        
    successful_cs = extra_cs + servs
    if not "-q" in flags:
        program.list_lxc_containers() 
    cs_s = concat_array(successful_cs)
    msg = (f" Contenedores '{cs_s}' inicializados\n")
    cmd_logger.info(msg)
    if len(successful_cs) > 0:
        cmd_logger.info(" Estableciendo conexiones " +
                                "entre contenedores y bridges...")
        platform.update_conexions()
        cmd_logger.info(" Conexiones establecidas\n")
        if "-l" in flags:
            c_names = list(map(lambda c: c.name, successful_cs))
            start(*c_names, options=options, flags=flags)
                 
# --------------------------------------------------------------------
def deploy(numServs:int, options={}, flags=[]):
    """Crea la plataforma del sistema-servidor, desplegando los 
    bridges y contenedores y conectandolos entre ellos (de la forma
    que se hayan definido estas conexiones en la carpeta program)

    Args:
        numServs (int): Numero de servidores a crear
        options (dict, optional): Opciones del comando crear
        flags (list, optional): Flags introducidos en el programa
    """
    if platform.is_deployed():
        msg = (" La plataforma de servidores ya ha sido desplegada, " 
              + "se debe destruir la anterior para crear otra nueva")
        cmd_logger.error(msg)
        return   
    cmd_logger.info(" Desplegando la plataforma de servidores...\n")
    # Creando bridges
    bgs = net_devices.get_bridges(numBridges=2)
    bgs_s = concat_array(bgs)
    cmd_logger.debug(f" Nombre de bridges (objetos) --> '{bgs_s}'")
    cmd_logger.info(" Creando bridges...")
    succesful_bgs = bridges.init(*bgs)
    if not "-q" in flags:
        program.list_lxc_bridges()
    bgs_s = concat_array(succesful_bgs)
    cmd_logger.info(f" Bridges '{bgs_s}' creados\n")
    # Creando contenedores
    dbimage = get_db_opts(options)
    lbimage, algorithm = get_lb_opts(options)
    if "--client" in options:
        climage, clname = get_cl_opts(options)
    simage, names = get_servers_opts(options)
    # Configurando e Iniciando contenedores de forma concurrente
    successful_cs = []
    with conc.ThreadPoolExecutor() as executor:
        threads = []
        db_thread = executor.submit(
            data_base.create_database, image=dbimage
        )
        threads.append(db_thread)
        lb_thread = executor.submit(
            load_balancer.create_lb, image=lbimage, balance=algorithm
        )
        threads.append(lb_thread)
        if "--client" in options:
            cl_thread = executor.submit(
                client.create_client, name=clname, image=climage
            )
            threads.append(cl_thread)
        servs_thread = executor.submit(
            servers.create_servers, numServs, *names, image=simage
        )
        threads.append(servs_thread)
        for thr in threads:
            container = thr.result()
            if type(container) is list:
                successful_cs += container
            elif container != None:
                successful_cs.append(container)
    # Mostramos la informacion y comprobamos flag de arranque
    if not "-q" in flags:
        program.list_lxc_containers() 
    cs_s = concat_array(successful_cs)
    msg = (f" Contenedores '{cs_s}' inicializados\n")
    cmd_logger.info(msg)
    if len(successful_cs) > 0:
        cmd_logger.info(" Estableciendo conexiones " +
                                "entre contenedores y bridges...")
        platform.update_conexions()
        cmd_logger.info(" Conexiones establecidas\n")
        if "-l" in flags:
            c_names = list(map(lambda c: c.name, successful_cs))
            start(*c_names, options=options, flags=flags)
    cmd_logger.info(" Plataforma de servidores desplegada")

# --------------------------------------------------------------------
def destroy(options={}, flags=[]):
    """Destruye la platafrma del sistema-servidor eliminando todos
    sus componenetes (bridges, contenedores y las conexiones entre
    ellos). Reutiliza el codigo de la funcion eliminar para eliminar
    los contenedores.

    Args:
        options (dict, optional): Opciones del comando destruir
        flags (list, optional): Flags introducidos en el programa
    """
    if not platform.is_deployed():
        msg = (" La plataforma de servidores no ha sido desplegada, " 
                 + "se debe crear una nueva antes de poder destruir")
        cmd_logger.error(msg)
        return
    if not "-y" in flags:
        msg = ("Se borrara por completo la infraestructura " + 
                "creada, contenedores, bridges y sus conexiones " + 
                    "aun podiendo estar arrancadas")
        print(msg)
        answer = str(input("¿Estas seguro?(y/n): "))
        if answer.lower() != "y":
            return
    cmd_logger.info(" Destruyendo plataforma...\n")
    # Eliminamos contenedores
    cs = register.load(containers.ID)
    if cs == None:
        cmd_logger.warning(" No existen contenedores en el programa\n")
    else:
        c_names = list(map(lambda c: c.name, cs))
        flags.append("-y") # Añadimos el flag -f
        remove(*c_names, flags=flags, skip_tags=[])
    # Eliminamos bridges
    bgs = register.load(bridges.ID)
    if bgs == None: 
        cmd_logger.warning(" No existen bridges en el programa")
    else:
        msg = f" Eliminando bridges '{concat_array(bgs)}'..."
        cmd_logger.info(msg)
        successful_bgs = bridges.delete(*bgs)
        if not "-q" in flags:
            program.list_lxc_bridges()
        bgs_s = concat_array(successful_bgs)
        msg = (f" Bridges '{bgs_s}' eliminados\n")
        cmd_logger.info(msg)  
    # Vemos si se ha eliminado todo  
    cs = register.load(containers.ID)
    bgs = register.load(bridges.ID) 
    if cs == None and bgs == None:
        register.remove("updates")
        cmd_logger.info(" Plataforma destruida")
    else:
        msg = (" Plataforma destruida parcialmente " +
                        "(se han encontrado dificultades)") 
        cmd_logger.error(msg)
            
# --------------------------------------------------------------------   
def change(options={}, flags={}):
    if "balance" in options:
        algorithm = options["balance"]["args"][0]
        load_balancer.change_algorithm(algorithm)

# --------------------------------------------------------------------       
def app(options={}, flags={}):
    if "markservs" in options:
        apps.mark_apps(*options["markservs"]["args"])
    elif "unmarkservs" in options:
        apps.mark_apps(*options["unmarkservs"]["args"], undo=True)
    elif "add" in options:
        apps.add_apps(*options["add"]["args"])
    elif "use" in options:
        servs = []
        if "--on" in options["use"]["options"]:
            servs = options["use"]["options"]["--on"]["args"]
        apps.use_app(options["use"]["args"][0], *servs)
        if "-m" in flags:
            apps.mark_apps()
    elif "setdef" in options:
        apps.set_default(options["setdef"]["args"][0])
    elif "unsetdef" in options:
        apps.unset_default()
    elif "list" in options:
        apps.list_apps()
    elif "rm" in options:
        app_names = options["rm"]["args"]
        if not "-y" in flags:
            default = apps.get_defaultapp()
            if default in app_names:
                print(f"La app '{default}' esta establecida como " + 
                    "default")
                question = "¿Eliminar la app de todas formas?(y/n): "
                answer = str(input(question))
                if answer.lower() != "y": return
        apps.remove_apps(*app_names)
    elif "emptyrep" in options:
        skip = []
        if not "-y" in flags:
            msg = ("Se eliminaran todas las aplicaciones del " +
                "repositorio local")
            print(msg)
            answer = str(input("¿Estas seguro?(y/n): "))
            if answer.lower() != "y": return
            answer = str(input("¿Eliminar tambien default?(y/n): "))
            if answer.lower() != "y": skip = [apps.get_defaultapp()]
        apps.clear_repository(skip=skip)
        
# -------------------------------------------------------------------- 
def show(options={}, flags={}):
    """Muestra informacion sobre el programa

    Args:
        choice (str): Indica que informacion se quiere mostrar
        options (dict, optional): Opciones del comando show
        flags (list, optional): Flags introducidos en el programa
    """
    if "diagram" in options:
        program.show_platform_diagram()
    elif "state" in options:
        platform.print_state()
    elif "dep" in options:
        program.show_dependencies()
    elif "info" in options:
        platform.print_info()
# --------------------------------------------------------------------
