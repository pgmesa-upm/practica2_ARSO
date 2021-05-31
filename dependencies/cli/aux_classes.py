
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
                 description:str=None, mandatory_opt=False, multi_opt=True):
        self.name = name
        self.extra_arg = extra_arg
        self.choices = choices
        self.default = default
        if description is None:
            description = ""
        self.description = description 
        self.mandatory = mandatory
        self.multi = multi
        self.mandatory_opt = mandatory_opt
        self.multi_opt = multi_opt
        self.options = {}
   
    def add_option(self, name:str, extra_arg:any=False, mandatory=False, 
                   multi=False, choices:list=None, default:any=None,
                   description:str=None):
        """Añade una opcion al comando. Una opcion es basicamente un 
        comando anidado dentro de otro, que necesita la existencia
        del comando principal para que este sea valido. Por eso los 
        parametros para definir una opcion son los mismos que para 
        definir un comando"""
        self.options[name] = Command(
            name,
            extra_arg=extra_arg, 
            mandatory=mandatory, 
            multi=multi,
            choices=choices, 
            default=default, 
            description=description
        )
    
    def add_option_ascmd(self, cmd):
        self.options[cmd.name] = cmd
     
    def __str__(self) -> str:
        """Define como se va a representar el comando en forma
        de string

        Returns:
            str: reperesentacion del objeto en forma string
        """
        return self.name 
    
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
        if description is None:
            description = ""
        self.description = description 
        
    def __str__(self) -> str:
        """Define como se va a representar el flag en forma
        de string

        Returns:
            str: reperesentacion del objeto en forma string
        """
        return self.name 