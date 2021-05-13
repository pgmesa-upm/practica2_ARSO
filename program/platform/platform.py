
from dependencies.utils.tools import pretty, objectlist_as_dict
import program.controllers.bridges as bridges
import program.controllers.containers as containers
import dependencies.register.register as register
from .machines import load_balancer, net_devices, servers, clients

# --------------------- FUNCIONES DE PLATAFORMA ------------------------
# --------------------------------------------------------------------
# Este fichero se encarga de proporcionar funciones especificas de la
# plataforma. Define como se van a conectar los contenedores con 
# los bridges (quien con quien) y muestra el estado actual de esta
# --------------------------------------------------------------------

def is_deployed():
    if register.load(bridges.ID) is None:
        return False
    return True

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
    cs = register.load(containers.ID)
    if cs == None: return
    # Actualizamos los servidores conectados al balanceador de carga
    if updates.get("cs_state", False):
        load_balancer.update_haproxycfg()
    # Realizamos las conexiones de los contenedores a los bridge
    bgs = register.load(bridges.ID)
    bgs_dict = objectlist_as_dict(
        bgs,
        key_attribute="name"
    )
    for c in cs:
        # Conectamos load balancer a los 2 bridges y el resto solo 
        # al bridge lxdbr0 (el que crea por defecto lxd) y cliente 
        # solo a lxdbr1
        if c.tag == load_balancer.TAG:
            if not c.connected_networks["eth0"]:
                bridges.attach(c.name, bgs_dict["lxdbr0"], "eth0")
            if not c.connected_networks["eth1"]:
                bridges.attach(c.name, bgs_dict["lxdbr1"], "eth1")
        elif c.tag == servers.TAG:
            if not c.connected_networks["eth0"]:
                bridges.attach(c.name, bgs_dict["lxdbr0"], "eth0")
        elif c.tag == clients.TAG:
            if not c.connected_networks["eth0"]:
                bridges.attach(c.name, bgs_dict["lxdbr1"], "eth0")
        containers.connect_to_networks(c)
    register.update("updates", {})
        
# --------------------------------------------------------------------
def print_state():
    """Muestra por consola el estado de los objetos del programa 
    (contenedores y bridges)"""
    cs = register.load(register_id=containers.ID)
    bgs = register.load(register_id=bridges.ID)
    if not is_deployed():
        print("--> La plataforma esta vacia, no ha sido desplegada")
    print("CONTENEDORES")
    if cs != None:
        for c in cs:
            print(pretty(c))
    else:
        print("No hay contenedores creados en la plataforma")
    print("BRIDGES")
    if bgs != None:       
        for b in bgs:
            print(pretty(b))
    else:
        print("No hay bridges creados en la plataforma")