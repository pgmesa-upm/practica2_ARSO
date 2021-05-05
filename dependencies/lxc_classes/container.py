
import subprocess
from contextlib import suppress


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
            container_image (str): Imagen con la que se va a crear 
                el contenedor
            tag (str, optional): Tag para diferenciar la funcionalidad
                de cada contenedor
        """
    def __init__(self, name:str, container_image:str, tag:str=""):
        
        self.name = str(name)
        self.container_image = container_image
        self.state = NOT_INIT
        self.tag = tag
        self.networks = {}
        
    def _run(self, cmd:list):
        """Ejecuta un comando mediante subprocess y controla los 
        errores que puedan surgir. Espera a que termine el proceso
        (Llamada bloqueante)

        Args:
            cmd (list): Comando a ejecutar

        Raises:
            LxcError: Si surge algun error ejecutando el comando
        """
        process = subprocess.run(
            cmd, 
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE # No queremos que salga en consola
        )
        outcome = process.returncode
        if outcome != 0:
            err_msg = (f" Fallo al ejecutar el comando {cmd}.\n" +
                            "Mensaje de error de lxc: ->")
            err_msg += process.stderr.decode().strip()[6:]
            raise LxcError(err_msg)    
        
    def add_to_network(self, eth:str, with_ip:str):
        """Añade el contenedor a una subred con la ip especificada

        Args:
            eth (str): Subred a la que se quiere conectar
            with_ip (str): Ip que se quiere utilizar
        """
        cmd = ["lxc","config","device","set", self.name,
                                        eth, "ipv4.address", with_ip]
        self._run(cmd)
        self.networks[eth] = with_ip

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
        subprocess.Popen([
            "xterm","-fa", "monaco", "-fs", "13", "-bg", "black",
            "-fg", "green", "-e", f"lxc exec {self.name} bash"
        ])
   
    def init(self):
        """Crea el contenedor

        Raises:
            LxcError: Si el contenedor ya se ha iniciado
        """
        if self.state != NOT_INIT:
            err = (f" {self.tag} '{self.name}' esta '{self.state}' " +
                                "y no puede ser inicializado de nuevo")
            raise LxcError(err)
        self._run(["lxc", "init", self.container_image, self.name])  
        self.state = STOPPED
        # Se limitan los recursos del contenedor 
        limits = {
            "cpu": ["limits.cpu.allowance", "40ms/200ms"], 
            "memory": ["limits.memory", "1024MB"],
            "cores": ["limits.cpu", "2"]
        }
        for l in limits: 
            with suppress(LxcError):
                self._run(["lxc", "config", "set", self.name] + limits[l])
        
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
        self._run(["lxc", "start", self.name])  
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
        self._run(["lxc", "stop", self.name, "--force"])  
        self.state = STOPPED
        
    def delete(self):
        """Elimina el contenedor

        Raises:
            LxcError: Si no esta parado 
        """
        if self.state != STOPPED:
            err = (f" {self.tag} '{self.name}' esta " +
                        f"'{self.state}' y no puede ser eliminado")
            raise LxcError(err)
        self._run(["lxc", "delete", self.name])  
        self.state = DELETED
    
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
        self._run(["lxc", "pause", self.name])  
        self.state = FROZEN
    
    def __str__(self):
        """Define como se va a representar el contenedor en forma
        de string

        Returns:
            str: reperesentacion del contenedor en forma string
        """
        return self.name
    
# --------------------------------------------------------------------        
class LxcError(Exception):
    """Excepcion personalizada para los errores al manipular 
    contenedores de lxc"""
    pass
# --------------------------------------------------------------------