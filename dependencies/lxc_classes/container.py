
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
        self.connected_networks = {}
        
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
        if self.connected_networks[eth]:
            err = (f" {self.tag} '{self.name}' ya se ha conectado " +
                   f"a la network '{eth}' con la ip {self.networks[eth]}")
            raise LxcError(err)
        cmd = ["lxc","config","device","set", self.name,
                eth, "ipv4.address", self.networks[eth]]
        self._run(cmd)
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
                
    def wait_for_startup(self):
        """Espera a que el contenedor haya terminado de arrancarse
        por completo. (Que todos los archivos, carpetas y
        configuraciones del contenedor hayan finalizado). Es util
        para cuando se quiere realizar operaciones nada mas se 
        hace un start del contenedor (puede haber fallos si no todos
        los archivos se han creado o no todo ha acabado de 
        configurarse)"""
        if self.state != RUNNING: return
        state = "initializing"
        while state != "running" and state != "degraded":
            ask_if_running = ["systemctl", "is-system-running"]
            process = subprocess.run(
                ["lxc", "exec", self.name, "--"] + ask_if_running,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE
            )
            state = process.stdout.decode().strip()
    
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