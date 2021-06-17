
# ------------------------ CLASES AUXILIARES -------------------------
# -------------------------------------------------------------------- 
# Clases auxiliares de la CLI que permiten definir las caracteristicas
# de los comandos y flags que va a tener el programa. Es una forma de
# almacenar la informacion para que procesarla luego sea mas comodo
# --------------------------------------------------------------------

class Command:
    """Inicializa el comando con las caracteristicas que se han
        definido

        Args:
            name (str): Nombre del comando
            extra_arg (any, optional): Indica si se permite algun 
                parametro extra
            mandatory (bool, optional): Indica si es obligatorio o no
                incluir el parametro extra. (extra_arg debe estar a 
                True)
            multi (bool, optional): Indica si se permiten multiples 
                parametros extra (numero indefinido) (extra_arg debe
                estar a True)
            choices (list, optional): Indica si el parametro extra o
                los parametros extra deben estar dentro de un conjunto
                de valores (extra_arg debe estar a True)
            default (any, optional): Indica el valor por defecto de un
                parametro extra en caso de que no se proporcione ninguno
                (extra_arg debe estar a True)
            description (str, optional): Da informacion de que hace el
                comando
        """
    def __init__(self, name:str, extra_arg:any=False, mandatory=False,
                 multi=False, choices:list=None, default:any=None,
                 description:str=None, mandatory_nested_cmd=False):
        self.name = name
        self.extra_arg = extra_arg
        self.choices = choices
        self.default = default
        self.description = description 
        self.mandatory = mandatory
        self.multi = multi
        self.mnc = mandatory_nested_cmd
        self.options = {}
        self.flags = {}
        self.nested_cmd = {}
        
    def nest_cmd(self, cmd):
        """AAnido un comando en el comando principal

        Args:
            cmd ([type]): [description]
        """
        if type(self) == Option:
            msg = ("No esta permitido que las opciones tengan " + 
            "otras opciones anidadas")
            raise CmdDefinitionError(msg)
        self.nested_cmd[cmd.name] = cmd
   
    def add_option(self, option):
        if type(self) == Option:
            msg = ("No esta permitido que las opciones tengan " + 
            "comandos anidados")
            raise CmdDefinitionError(msg)
        self.options[option.name] = option
        
    def add_flag(self, flag):
        if type(self) == Option:
            msg = ("No esta permitido que las opciones tengan " + 
            "flags aninados")
            raise CmdDefinitionError(msg)
        self.flags[flag.name] = flag
     
    def __str__(self) -> str:
        """Define como se va a representar el comando en forma
        de string

        Returns:
            str: reperesentacion del objeto en forma string
        """
        return self.name 
    
# --------------------------------------------------------------------  
class Option(Command):
    """Una opcion es un comando especial que no puede tener comandos 
        anidados y que permite aportar funcionalidades al comando principal"""
    def __init__(self, name:str, extra_arg:any=False, mandatory=False,
                 multi=False, choices:list=None, default:any=None,
                 description:str=None):
        super().__init__(
            name, extra_arg=extra_arg, mandatory=mandatory, multi=multi,
            choices=choices, default=default, description=description)
    
# --------------------------------------------------------------------     
class Flag:
    """Inicializa el flag con las caracteristicas que se han
        definido

        Args:
            name (str): Nombre del flag
            notCompatibleWithFlags (list, optional): Indica los nombres
                de los flags con los que no es compatible (no pueden 
                aparecer juntos en la linea de comandos)
            description (str, optional): Informa de la funcionalidad
                del flag
        """
    def __init__(self, name:str, notCompatibleWithFlags:list=[], 
                 description:str=None):
        self.name = name
        self.ncwf = notCompatibleWithFlags + [self.name]
        self.description = description
        
    def __str__(self) -> str:
        """Define como se va a representar el flag en forma
        de string

        Returns:
            str: reperesentacion del objeto en forma string
        """
        return self.name 

# --------------------------------------------------------------------
class CmdDefinitionError(Exception):
    pass