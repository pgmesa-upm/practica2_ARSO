
from dependencies.register import register
from program.controllers import containers, bridges
from dependencies.lxc.lxc_classes.bridge import Bridge

# ----------------------- DISPOSITIVOS DE RED ------------------------
# --------------------------------------------------------------------
# Este fichero se encarga de proporcionar funciones para crear y 
# configurar los objetos de los bridges que se van a utilizar en la 
# plataforma
# --------------------------------------------------------------------

# -------------------------------------------------------------------
def get_bridges(numBridges:int) -> list:
    """Devuelve los objetos de los bridges que se vayan a crear 
    configurados

    Args:
        numBridges (int): Numero de bridges a crear

    Returns:
        list: lista de objetos de tipo Bridge
    """
    bgs = []
    for i in range(numBridges):
        b_name = f"lxdbr{i}"
        b = Bridge(
            b_name, 
            ipv4_nat=True,
            ipv4_addr=f"10.0.{i}.1/24"
        )
        bgs.append(b)
    return bgs

def update_conexions():
    """Revisa si algun contenedor ha sido eliminado para 
    eliminarlo del bridge al que estaba asociado (bridge.used_by)"""
    bgs = register.load(register_id=bridges.ID)
    if bgs == None: return
    cs = register.load(register_id=containers.ID)
    if cs == None:
        names_existing_cs = []
    else:
        names_existing_cs = list(map(lambda c: c.name, cs))
    
    for b in bgs:
        deleted = []
        for c_name in b.used_by:
            if c_name not in names_existing_cs:
                deleted.append(c_name)
        for d in deleted:
            b.used_by.remove(d)
    register.update(bridges.ID, bgs)