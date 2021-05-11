
import logging

from .reused_code import target_containers
from program.controllers import bridges, containers
from program.platform.machines import (
    servers, 
    load_balancer, 
    net_devices,
    clients,
    data_base
)
from program import program
import dependencies.register.register as register
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
def arrancar(*target_cs, options={}, flags=[]):
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
        
# --------------------------------------------------------------------
@target_containers(cmd_logger) 
def parar(*target_cs, options={}, flags=[]):
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
def pausar(*target_cs, options={}, flags=[]):
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
def eliminar(*target_cs, options={}, flags=[],
            skip_tags=[load_balancer.TAG, clients.TAG]): 
    """Elimina los contenedores que se enceuntren en target_cs.
    Por defecto, esta funcion solo elimina los contenedores que 
    sean servidores

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
                msg = (f" El contenedor '{c}' no es un servidor " + 
                        "(solo se pueden eliminar servidores)")
                cmd_logger.error(msg)  
                continue
            valid_cs.append(c)
        if len(valid_cs) == 0: return
        target_cs = valid_cs
    if not "-f" in flags:
        print("Se eliminaran los servidores:" +
                    f" '{concat_array(target_cs)}'")
        answer = str(input("¿Estas seguro?(y/n): "))
        if answer.lower() != "y":
            return
    # Eliminamos los existentes que nos hayan indicado
    msg = f" Eliminando contenedores '{concat_array(target_cs)}'..."
    cmd_logger.info(msg)
    succesful_cs = containers.delete(*target_cs)
    # Actualizamos los contenedores que estan asociados a cada bridge
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
def añadir(numServs:int, options={}, flags=[], extra_cs=[]):
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
        msg = (" La plataforma de servidores no ha sido " +
                    "desplegada, se debe crear una nueva antes " +
                        "de añadir los servidores")
        cmd_logger.error(msg)
        return
    existent_cs = register.load(containers.ID)
    if existent_cs != None:
        ex_s = filter(lambda cs: cs.tag == servers.TAG, existent_cs)
        num = len(list(ex_s))
        if num + numServs > 5: 
            msg = (f" La plataforma no admite mas de 5 servidores. " +
                    f"Actualmente existen {num}, no se " +
                            f"puede añadir {numServs} mas")
            cmd_logger.error(msg)
            return
    # Creando contenedores 
        # Elegimos la imagen con la que se van a crear
    simage = servers.default_image
    if "--image" in options:
        simage = options["--image"][0]
    if "--simage" in options:
        simage = options["--simage"][0]
        
    if "--name" in options:   
        names = options["--name"]
        cs = extra_cs + servers.get_servers(
            numServs, 
            *names, 
            image=simage
        )
    else:
        cs = extra_cs + servers.get_servers(
            numServs,
            image=simage
        )
    cs_s = concat_array(cs)
    msg = f" Nombre de contenedores (objetos) --> '{cs_s}'"
    cmd_logger.debug(msg)
    launch = True if "-l" in flags else False
    show = True if not launch and "-q" not in flags else False
    cmd_logger.debug(f" Launch --> {launch} | show --> {show}")
    cmd_logger.info(f" Inicializando contenedores '{cs_s}'...")
    successful_cs = containers.init(*cs)
    if not "-q" in flags:
        program.list_lxc_containers() 
    cs_s = concat_array(successful_cs)
    msg = (f" Contenedores '{cs_s}' inicializados\n")
    cmd_logger.info(msg)
    if len(successful_cs) != 0:     
        # Estableciendo conexiones
        cmd_logger.info(" Estableciendo conexiones " +
                                "entre contenedores y bridges...")
        platform.update_conexions()
        cmd_logger.info(" Conexiones establecidas\n")
        # Arrancamos los contenedores creados con exito 
        # (si nos lo han pedido) 
        if successful_cs != None and launch:
            c_names = list(map(lambda c: c.name, successful_cs))
            arrancar(*c_names, flags=flags) 
                 
# --------------------------------------------------------------------
def crear(numServs:int, options={}, flags=[]):
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
        # Elegimos la imagen con la que se van a crear
    lbimage = None; climage = None
    if "--image" in options:
        lbimage = options["--image"][0]
        climage = options["--climage"][0]
    if "--lbimage" in options:
        lbimage = options["--lbimage"][0]
    if "--climage" in options:
        climage = options["--climage"][0]
    lb = load_balancer.get_lb(image=lbimage)
    cl = clients.get_client(image=climage)
    añadir(numServs, options=options, flags=flags, extra_cs=[lb, cl]) 
    cmd_logger.info(" Plataforma de servidores desplegada")

# --------------------------------------------------------------------
def destruir(options={}, flags=[]):
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
    if not "-f" in flags:
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
        flags.append("-f") # Añadimos el flag -f
        eliminar(*c_names, flags=flags, skip_tags=[])
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
        cmd_logger.info(" Plataforma destruida")
    else:
        msg = (" Plataforma destruida parcialmente " +
                        "(se han encontrado dificultades)") 
        cmd_logger.error(msg)
            
# --------------------------------------------------------------------   
def show(choice:str, options={}, flags={}):
    """Muestra informacion sobre el programa

    Args:
        choice (str): Indica que informacion se quiere mostrar
        options (dict, optional): Opciones del comando show
        flags (list, optional): Flags introducidos en el programa
    """
    if choice == "diagram":
        program.show_platform_diagram()
    elif choice == "state":
        platform.print_state()
    elif choice == "dependencies":
        program.show_dependencies()
        
# --------------------------------------------------------------------