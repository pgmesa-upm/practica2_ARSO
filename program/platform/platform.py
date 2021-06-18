
import logging
from program.platform.machines import data_base

from dependencies.utils.tools import (
    pretty, objectlist_as_dict, remove_many, remove_ntimes
)
from dependencies.lxc import lxc
from program.controllers import containers, bridges
from dependencies.register import register
from .machines import load_balancer, net_devices, servers, client

# --------------------- FUNCIONES DE PLATAFORMA ------------------------
# --------------------------------------------------------------------
# Este fichero se encarga de proporcionar funciones especificas de la
# plataforma. Define como se van a conectar los contenedores con 
# los bridges (quien con quien) y muestra el estado actual de esta
# --------------------------------------------------------------------

plt_logger = logging.getLogger(__name__)
# Imagen por defecto sobre la que se va a realizar la configuracion
# de los contenedores
default_image = "ubuntu:18.04"
# --------------------------------------------------------------------
def is_deployed():
    if register.load(bridges.ID) is None:
        return False
    return True

def have_containers():
    if register.load(containers.ID) is None:
        return False
    return True

def search_cs(cs_names:list=[], tags:list=[], skip:list=[], talk:bool=True):
    existing_cs = register.load(containers.ID)
    if existing_cs is None: 
        plt_logger.error(" No existen contenedores en el programa")
        return None
    check_tags = True
    if len(tags) == 0: check_tags = False
    all_cs = len(cs_names) == 0
    if all_cs:
        cs_names = list(map(str, existing_cs))
    found = []; skipped = False
    for c_name in cs_names:
        for ex_c in existing_cs:
            if c_name == ex_c.name:
                if not check_tags or ex_c.tag in tags:
                    if not ex_c.name in skip:
                        found.append(ex_c)
                    else:
                        skipped = True
                elif talk:
                    msg = f" El contenedor '{c_name}' no es del tipo {tags}"
                    plt_logger.error(msg)
                break
        else:
            if talk:
                msg = f" El contenedor '{c_name}' no se existe en el programa"
                plt_logger.error(msg)
    if len(found) == 0:
        if all_cs and not skipped:
            msg = f" No existen {tags} para realizar la operacion"
            plt_logger.error(msg)
        else:
            msg = (f" No se han seleccionado contenedores para " + 
                    "realizar la operacion")
            plt_logger.error(msg)
        return None
    return found
    
# --------------------------------------------------------------------
def update_conexions():
    """ Se encarga de conectar los contenedores con los bridge. Mira 
    todos los contenedores creados (que estan en el registro) y si
    no se le ha asociado a ninguna network todavia lo conecta a una de
    las existentes dependiendo del tag que tenga (Los servidores a
    bridge 0, los clientes al bridge 1 y load balancer a los 2)"""
    
    # Si la plataforma no se ha desplegado salimos
    if not is_deployed(): return
    updates = register.load("updates")
    # Actualizamos los contenedores conectados a los bridges
    if updates.get("cs_num", False):
        net_devices.update_conexions()
    # Miramos si hay contenedores en el programa (si no hay, ni si
    # quiera el lb, es que los han eliminado desde fuera)
    if not have_containers(): 
        register.update("updates", {})
        return
    # Actualizamos los servidores conectados al balanceador de carga
    if updates.get("s_state", False):
        lb = load_balancer.get_lb()
        load_balancer.update_haproxycfg(lb, reset_on_fail=False)
    # Realizamos las conexiones de los contenedores a los bridge
    cs = register.load(containers.ID)
    bgs = register.load(bridges.ID)
    bgs_dict = objectlist_as_dict(
        bgs,
        key_attribute="name"
    )
    for c in cs:
        # Conectamos load balancer a los 2 bridges y el resto solo 
        # al bridge lxdbr0 (el que crea por defecto lxd) y cliente 
        # solo a lxdbr1
        lxdbr0_exists = bgs_dict.get("lxdbr0", None) is not None
        lxdbr1_exists = bgs_dict.get("lxdbr1", None) is not None
        if c.tag == load_balancer.TAG:
            if not c.connected_networks["eth0"]:
                if not lxdbr0_exists:
                    err = (f"Error al conectar {c.tag} '{c.name}' a "
                             + "bridge lxdbr0. Este bridge no existe")
                    plt_logger.error(err)
                    continue
                bridges.attach(c.name, bgs_dict["lxdbr0"], "eth0")
            if not c.connected_networks["eth1"]:
                if not lxdbr1_exists:
                    err = (f"Error al conectar {c.tag} '{c.name}' a "
                             + "bridge lxdbr1. Este bridge no existe")
                    plt_logger.error(err)
                    continue
                bridges.attach(c.name, bgs_dict["lxdbr1"], "eth1")
        elif c.tag == servers.TAG or c.tag == data_base.TAG:
            if not c.connected_networks["eth0"]:
                if not lxdbr0_exists:
                    err = (f"Error al conectar {c.tag} '{c.name}' a "
                             + "bridge lxdbr0. Este bridge no existe")
                    plt_logger.error(err)
                    continue
                bridges.attach(c.name, bgs_dict["lxdbr0"], "eth0")
        elif c.tag == client.TAG:
            if not c.connected_networks["eth0"]:
                if not lxdbr1_exists:
                    err = (f"Error al conectar {c.tag} '{c.name}' a "
                             + "bridge lxdbr1. Este bridge no existe")
                    plt_logger.error(err)
                    continue
                bridges.attach(c.name, bgs_dict["lxdbr1"], "eth0")
        containers.connect_to_networks(c)
    register.update("updates", {})
        
# --------------------------------------------------------------------
def print_state(machines:list=[]):
    """Muestra por consola el estado de los objetos del programa 
    (contenedores y bridges)"""
    if not is_deployed():
        print("--> La plataforma esta vacia, no ha sido desplegada")
    # Vemos los contenedores a mostrar
    ex_cs = register.load(register_id=containers.ID)
    ex_bgs = register.load(register_id=bridges.ID)
    if len(machines) > 0:
        cs = []
        for c in ex_cs:
            if c.name in machines:
                cs.append(c)
                remove_ntimes(machines, c.name)
        # Vemos los bridges a mostrar
        bgs = []
        for bg in ex_bgs:
            if bg.name in machines:
                bgs.append(bg)
                remove_ntimes(machines, bg.name)
    else:
        cs = ex_cs; bgs = ex_bgs
    # Las que sigan quedando en la lista es que no existen en el programa
    for m in machines:
        msg = f" La maquina '{m}' no existe en el programa"
        plt_logger.error(msg)
    if cs is None or len(cs) > 0:
        print(" + CONTENEDORES")
        if cs is not None:
            pairs = [
                ("name", "tag"), 
                ("state", "started_up"), 
                ("networks", "connected_networks"),
            ]
            attrs_order = [
                "name", "state", "networks", "base_image", "marked"
            ]
            for c in cs:
                extra_pairs = []
                if c.tag == servers.TAG:
                    extra_pairs = [("base_image", "app")]
                elif c.tag == load_balancer.TAG:
                    extra_pairs = [("base_image", "algorithm")]
                print(pretty(
                    c, *(pairs+extra_pairs), firstcolum_order=attrs_order
                ))
        else:
            print("     No hay contenedores creados en la plataforma")
    if bgs is None or len(bgs) > 0:
        print(" + BRIDGES")
        if bgs is not None:       
            for b in bgs:
                print(pretty(b))
        else:
            print("     No hay bridges creados en la plataforma")

def print_info():
    print("""
    Al desplegarse la plataforma se crean 2 puentes virtuales (lxdbr0
    y lxdbr1), una base de datos MongoDB y un balanceador haproxy para 
    distribuir la carga del tráfico entre los servidores. Tambien se
    crean el numero de servidores tomcat8 especificados y un cliente 
    lynx en caso de que se indique. A la subnet del lxdbr0 se conectan 
    los servidores, la base de datos y el balanceador y al lxdbr1 se
    conectan los clientes y el balanceador (introducir 'show diagram' 
    para mas informacion sobre la infraestructura). El balanceador se 
    encarga de manejar a que servidor se va a conectar el cliente sin 
    que este sepa su direccion ip (transparecia, el cliente no sabe a 
    cual se esta conectando) (El comando 'app markservs' permite
    distinguirlos).
    
    Por defecto, el programa configura una imagen con tomcat8 para los 
    servidores, una imagen haproxy (con dos tarjetas de red) para el 
    balanceador, una base de datos MongoDB y un cliente lynx (si se
    indica). La plataforma solo admite un cliente contenedor y 5
    servidores. Un servidor tomcat admite 200 peticiones simultaneas 
    de clientes por defecto, por lo que la plataforma soportara 1000 
    peticiones/conexiones simultaneas a los recursos (aplicaciones) 
    disponibles que se hayan distribuido en los servidores.
    
     + ¡IMPORTANTE!
    Si se quisiera especificar una imagen distinta para alguno de los
    componenetes, deben cumplir los siguientes requisitos para el 
    correcto funcionamiento del programa
    --> Imagen de Servidores: Debe tener tomcat8 instalado
    --> Imagen de Balanceador: Debe tener haproxy instalado y dos 
            tarjetas de red para conectarse a cada uno de los bridges
    --> Imagen de Base de Datos: Se puede instalar cualquier base de
            datos, mientras que la aplicacion web que se utilice en
            los servidores (carpeta ROOT) sepa como interactuar con 
            ella (db_ip_default=10.0.0.20). 
    --> Imagen de cliente: Se puede utilizar cualquier imagen ya que 
            este no tiene un impacto en el funcionamiento del programa
            (solo sirve para simular una conexion a los servidores)
    """)
  
# --------------------------------------------------------------------
def is_imageconfig_needed(reg_id_ofimage:str) -> bool:
    reg_id = reg_id_ofimage
    img_saved = register.load(reg_id)
    if img_saved is None:
        return True
    else:
        # Comprobamos que la imagen no se haya borrado en lxc
        fgp = img_saved["fingerprint"]
        msg = (f" Imagen anterior guardada en " + 
                        f"registro '{reg_id}' -> '{fgp}'")
        plt_logger.debug(msg)
        images = lxc.lxc_image_list()
        if fgp in images:
            # Vemos el alias de la imagen por si se ha modificado 
            alias = images[fgp]["ALIAS"] 
            image_info = {"alias": alias, "fingerprint": fgp}
            register.update(reg_id, image_info, override=True)
            msg = (" Alias actual de la imagen " + 
                    f"guardada en registro {reg_id} -> '{alias}'")
            plt_logger.debug(msg)
            return False
        else:
            # Como se ha eliminado creamos otra nueva
            msg = (f" Imagen guardada en registro '{reg_id}' se ha " + 
                    "borrado desde fuera del programa")
            plt_logger.debug(msg)
            register.remove(reg_id)
            return True    
# --------------------------------------------------------------------
