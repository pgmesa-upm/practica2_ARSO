
from ...lxc import lxc
from ..lxc import LxcNetworkError

class Bridge:
    """Clase envoltorio que permite controlar un bridge de lxc

        Args:
            name (str): Nombre del Bridge
            ipv4_nat (bool, optional): Indica si va a tener ipv4
            ipv4_addr (str, optional): Especifica la ipv4 que va a 
                tener el bridge y el identificador de red que van a 
                tener las ips de los contenedores que se conecten al el
            ipv6_nat (bool, optional): Indica si va a tener ipv6
            ipv6_addr (str, optional): Especifica la ipv6 que va a 
                tener el bridge y el identificador de red que van a 
                tener las ips de los contenedores que se conecten al el
        """
    def __init__(self, name:str,
                 ipv4_nat:bool=False, ipv4_addr:str=None,
                 ipv6_nat:bool=False, ipv6_addr:str=None):
        self.name = str(name)
        self.ipv4_nat = "true" if ipv4_nat == True else "false"
        self.ipv4_addr = ipv4_addr if ipv4_addr != None else "none"
        self.ipv6_nat = "true" if ipv6_nat == True else "false"
        self.ipv6_addr = ipv6_addr if ipv6_addr != None else "none"
        self.used_by = []
  
    def add_container(self, cs_name:str, with_eth:str):
        """Añade un contenedor a la red del bridge

        Args:
            cs_name (str): Nombre del contenedor a añadir
        """
        cmd = [
            "lxc", "network", "attach" ,
            self.name, cs_name, with_eth
        ]
        lxc.run(cmd)
        self.used_by.append(cs_name)
    
    def create(self):
        """Crea el bridge y si ya esta creado o se ha creado
        con exito tambien lo configura"""
        try:
            lxc.run(["lxc", "network", "create", self.name])
        except LxcNetworkError as err:
            err_msg = str(err)
            if "already exists" in err_msg:
                self._configure_ips()
            raise LxcNetworkError(err)
        else:
            self._configure_ips()
                
    def _configure_ips (self):
        set_ = ["lxc", "network", "set", self.name] 
        lxc.run(set_ + ["ipv4.nat", self.ipv4_nat])
        lxc.run(set_ + ["ipv4.address", self.ipv4_addr])
        lxc.run(set_ + ["ipv6.nat", self.ipv6_nat])
        lxc.run(set_ + ["ipv6.address", self.ipv6_addr])
    
    def delete(self):
        """Elimina el bridge

        Raises:
            LxcNetworkError: Si el bridge esta siendo usado por
                algun contenedor
        """
        if len(self.used_by) == 0:
            cmd = ["lxc", "network", "delete", self.name]
            lxc.run(cmd)
        else:
            err = (f" El bridge '{self.name}' esta siendo usado " +
                  f"por: {self.used_by} y no se puede eliminar")
            raise LxcNetworkError(err)
        
    def __str__(self):
        return self.name
# --------------------------------------------------------------------
