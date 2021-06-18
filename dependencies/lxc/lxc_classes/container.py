
from contextlib import suppress
from time import sleep

from ...lxc import lxc
from ..lxc import LxcError

# Posibles estados de los contenedores
NOT_INIT = "NOT INITIALIZED"
STOPPED = "STOPPED"
FROZEN = "FROZEN"
RUNNING = "RUNNING"
DELETED = "DELETED"

class Container:
    """Clase envoltorio que permite controlar un contenedor de lxc

        Args:
            name (str): Nombre del contenedor
            image (str): Imagen con la que se va a crear 
                el contenedor
            tag (str, optional): Tag para diferenciar la funcionalidad
                de cada contenedor
        """
    def __init__(self, name:str, base_image:str, tag:str=""):
        self.name = str(name)
        self.base_image = base_image
        self.state = NOT_INIT
        self.started_up = False
        self.tag = tag
        self.networks = {}
        self.connected_networks = {}
        
    def execute(self, cmd:list, stdout=True, stderr=True):
        """Ejecuta un comando en el interior del contenedor

        Args:
            cmd (list): Comando a ejecutar
        """
        self.wait_for_startup()
        cmd = ["lxc", "exec", self.name, "--"] + cmd
        out = lxc.run(cmd, stdout=stdout, stderr=stderr)  
        return out  
        
    def add_to_network(self, eth:str, with_ip:str=None):
        """Añade una tarjeta de red para conectarse a una red (se 
        conectara al bridge/net a la que se haya asociado la tarjeta)
        con la ip especificada

        Args:
            eth (str): Tarjeta de red 
            with_ip (str): Ip que se quiere utilizar
        """
        self.networks[eth] = with_ip
        self.connected_networks[eth] = False

    def connect_to_network(self, eth):
        if eth not in self.networks:
            err = (f" La tarjeta de red '{eth}' no se encuentra " + 
                   f"en el {self.tag} '{self.name}'")
            raise LxcError(err)
        if self.connected_networks[eth] is None:
            err = (f" La tarjeta de red {eth} del {self.tag} " +
                   f"'{self.name}' no tiene asignada una ip con la que " +
                   "conectarse a la subred de su bridge asociado")
            raise LxcError(err)
        elif self.connected_networks[eth]:
            err = (f" {self.tag} '{self.name}' ya se ha conectado " +
                   f"a la network '{eth}' con la ip {self.networks[eth]}")
            raise LxcError(err)
        cmd = ["lxc","config","device","set", self.name,
                eth, "ipv4.address", self.networks[eth]]
        lxc.run(cmd)
        self.connected_networks[eth] = True
    
    def open_terminal(self):
        """Abre la terminal del contenedor (utiliza 
        xterm -> instalar)

        Raises:
            LxcError: Si no esta arrancado
        """
        if self.state != RUNNING:
            err = (f" {self.tag} '{self.name}' esta " +
                        f"'{self.state}' y no puede abrir la terminal")
            raise LxcError(err)
        lxc.Popen([
            "xterm","-fa", "monaco", "-fs", "13", "-bg", "black",
            "-fg", "green", "-e", f"lxc exec {self.name} bash"
        ])
                
    def refresh(self):
        if self.state != RUNNING: 
            self.started_up = False
            return
        cmd = ["lxc", "exec", self.name, "--"]
        ask_if_running = ["systemctl", "is-system-running"]
        try:
            out = lxc.run(cmd + ask_if_running, stderr=False)
        except LxcError as err:
            out = str(err)
        state = out.strip()
        risky_cond = state == "starting"
        if state == "running" or state == "degraded" or risky_cond:
            self.started_up = True
            return
        self.started_up = False
                
    def wait_for_startup(self):
        """Espera a que el contenedor haya terminado de arrancarse
        por completo. (Que todos los archivos, carpetas y
        configuraciones del contenedor hayan finalizado). Es util
        para cuando se quiere realizar operaciones nada mas se 
        hace un start del contenedor (puede haber fallos si no todos
        los archivos se han creado o no todo ha acabado de 
        configurarse)"""
        if self.state != RUNNING: 
            err = (f"El contenedor '{self.name}' no se ha arrancado")
            raise LxcError(err)
        while not self.started_up:
            self.refresh()
    
    def update_apt(self):
        self.execute(["apt-get","update"])
    
    def install(self, module:str):
        self.execute(["apt-get","install","-y",module])
        
    def publish(self, alias:str=None):
        if self.state != STOPPED:
            err = (f" {self.tag} '{self.name}' debe estar parado para " + 
                   "publicar su imagen")
            raise LxcError(err)
        cmd = ["lxc", "publish", self.name]
        if alias is not None:
            cmd = cmd + ["--alias", alias]
        lxc.run(cmd)

    def push(self, file:str, to_path:str):
        self.wait_for_startup()
        if to_path.startswith("/"):
            to_path = to_path[1:]
        c_path = f"{self.name}/{to_path}"
        #"-r" se añade para que se haga de forma recursiva por si 
        # se pasa una carpeta en vez de un fichero
        lxc.run(["lxc", "file", "push", "-r", file, c_path])
    
    def pull(self, file_path:str, in_path:str):
        # Se puede introducir en file "." para que se descarguen todos 
        # los archivos de la carpeta
        self.wait_for_startup()
        if file_path.startswith("/"):
            file_path = file_path[1:]
        c_path = f"{self.name}/{file_path}"
        #"-r" se añade para que se haga de forma recursiva por si 
        # se pasa una carpeta en vez de un fichero
        lxc.run(["lxc", "file", "pull", "-r",  c_path, in_path])
    
    def init(self):
        """Crea el contenedor

        Raises:
            LxcError: Si el contenedor ya se ha iniciado
        """
        if self.state != NOT_INIT:
            err = (f" {self.tag} '{self.name}' esta '{self.state}' " +
                                "y no puede ser inicializado de nuevo")
            raise LxcError(err)
        lxc.run(["lxc", "init", self.base_image, self.name])  
        self.state = STOPPED
        # Se limitan los recursos del contenedor 
        limits = {
            "cpu": ["limits.cpu.allowance", "40ms/200ms"], 
            "memory": ["limits.memory", "1024MB"],
            "cores": ["limits.cpu", "2"]
        }
        for l in limits: 
            with suppress(LxcError):
                lxc.run(["lxc", "config", "set", self.name] + limits[l])
                
    def restart(self):
        if self.state != RUNNING:
            err = f" {self.tag} '{self.name}' no esta arrancado"
            raise LxcError(err)
        self.stop()
        self.start()
        
    def start(self):
        """Arranca el contenedor

        Raises:
            LxcError: Si ya esta arrancado
            LxcError: Si no se puede arrancar
        """
        if self.state == RUNNING:
            err = f" {self.tag} '{self.name}' ya esta arrancado"
            raise LxcError(err)
        elif self.state == DELETED and self.state == NOT_INIT:
            err = (f" {self.tag} '{self.name}' esta " +
                        f"'{self.state}' y no puede ser arrancado")
            raise LxcError(err)
        lxc.run(["lxc", "start", self.name])  
        self.state = RUNNING
        
    def stop(self):
        """Para el contenedor

        Raises:
            LxcError: Si ya esta parado
            LxcError: Si no puede pararse
        """
        if self.state == STOPPED:
            err = (f" {self.tag} '{self.name}' ya esta detenido")
            raise LxcError(err)
        elif self.state == DELETED and self.state == NOT_INIT:
            err = (f" {self.tag} '{self.name}' esta " +
                        f"'{self.state}' y no puede ser detenido")
            raise LxcError()
        lxc.run(["lxc", "stop", self.name, "--force"])  
        self.state = STOPPED
        self.started_up = False
        
    def delete(self):
        """Elimina el contenedor

        Raises:
            LxcError: Si no esta parado 
        """
        if self.state != STOPPED:
            err = (f" {self.tag} '{self.name}' esta " +
                        f"'{self.state}' y no puede ser eliminado")
            raise LxcError(err)
        lxc.run(["lxc", "delete", self.name])  
        self.state = DELETED
        self.started_up = False
    
    def pause(self):
        """Pausa el contenedor

        Raises:
            LxcError: Si ya esta pausado
            LxcError: Si no se puede pausar
        """
        if self.state == FROZEN:
            err = (f" {self.tag} '{self.name}' ya esta pausado")
            raise LxcError(err)
        elif self.state != RUNNING:
            err = (f" {self.tag} '{self.name}' esta " +
                        f"'{self.state}' y no puede ser pausado")
            raise LxcError(err)
        lxc.run(["lxc", "pause", self.name])  
        self.state = FROZEN
        self.started_up = False
    
    def __str__(self):
        """Define como se va a representar el contenedor en forma
        de string

        Returns:
            str: reperesentacion del contenedor en forma string
        """
        return self.name
# --------------------------------------------------------------------        
