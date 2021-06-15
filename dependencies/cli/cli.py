
from .aux_classes import Command, Flag
from .cli_utils import format_str


class Cli:
    """Interfaz que se encarga de controlar que la linea de comandos
    introducida en un programa es correcta, (mira que todos los flags y 
    comandos introducidos por terminal son correctos y compatibles).
    Hace falta una configuracion previa (definir que comandos y flags
    que va a tener el programa y sus caracteristicas)"""
    def __init__(self, pass_on_help=True):
        self.commands = {}
        self.global_flags = {"-h": Flag(
            "-h", 
            description=("shows information about a command or all of " +
                        "them if a valid one is not introduced")
        )}
        self.pass_on_help = pass_on_help
        self.printed = False
        
    def add_command(self, command:Command):
        """Añade un nuevo comando 

        Args:
            command (Command): Comando a añadir
        """
        self.commands[command.name] = command 
    
    def add_global_flag(self, flag:Flag):
        """Añade un nuevo Flag

        Args:
            flag (Flag): Flag a añadir
        """
        self.global_flags[flag.name] = flag
        
    def process_cmdline(self, args:list) -> dict:
        """Procesa los argumentos que se pasan como parametro. Informa 
        de si estos son validos o no en base a los comandos y flags 
        que conformen la cli.

        Args:
            args (list): Linea de comandos a procesar

        Raises:
            CmdLineError: Si no se han proporcionado argumentos
            CmdLineError: Si el comando no es correcto

        Returns:
            dict: diccionario con el comando, las opciones del comando
                y los flags como claves y los parametros que se les 
                hayan pasado como valores (si esque se les ha pasado
                alguno)
        """
        args.pop(0) # Eliminamos el nombre del programa
        processed_line = {
            "cmd": None,"args": [], 
            "options": {}, "flags": [],
            "gflags": []
        }
        # Procesamos flags globales    
        gflags = []
        while len(args) > 0 and args[0] in self.global_flags:
            gflags.append(args.pop(0))
        if "-h" in gflags:
            self.print_help()
            if self.pass_on_help:
                return None
            gflags.remove("-h")
        self._check_global_flags(gflags)
        processed_line["gflags"] = gflags
        # Revisamos si alguno de los comandos validos esta en la 
        # linea de comandos introducida
        for cmd in self.commands.values():    
            if len(args) == 0:
                err_msg = "No se ha introducido ningun comando"
                raise CmdLineError(_help=(not self.printed), msg=err_msg)
            if args[0] == cmd.name:
                try:
                    # Vemos si cada parte es válida y la guardamos en 
                    # un diccionario
                    processed_line["cmd"] = cmd.name
                    parts = self._split_line(cmd, args)
                    # Procesamos flags del comando
                    flags = self._check_flags(cmd, parts[cmd.name])
                    processed_line["flags"] = flags
                    # Procesamos parametros del comando
                    self._check_opt_restrictions(cmd, parts)
                    params = self._check_command(cmd, parts.pop(cmd.name))
                    processed_line["args"] = params
                    # Procesamos las opciones del comando principal y de cada
                    # opcion de forma recursiva
                    for opt_name in parts:
                        opt = cmd.options[opt_name]
                        options = self._process_options(opt, parts[opt_name])
                        processed_line["options"][opt_name] = options
                    return processed_line
                except HelpException:
                    return None
        err_msg = f"El comando '{args[0]}' no se reconoce"
        raise CmdLineError(_help=(not self.printed), msg=err_msg)
    
    def _process_options(self, opt:Command, args:list):
        parts = self._split_line(opt, [opt.name] + args)
        processed_line = {"args": [], "options": {}, "flags": []}
        # Procesamos flags de la opcion
        flags = self._check_flags(opt, parts[opt.name])
        processed_line["flags"] = flags
        # Procesamos parametros de la opcion
        self._check_opt_restrictions(opt, parts)
        params = self._check_command(opt, parts.pop(opt.name))
        processed_line["args"] = params
        for opt_name in parts:
            sub_opt = opt.options[opt_name]
            options = self._process_options(sub_opt, parts[opt_name])
            processed_line["options"][sub_opt.name] = options
        return processed_line
    
    def _split_line(self, cmd:Command, args:list) -> dict:
        # Separamos por partes la linea de comandos
        ant = args[0]; parts = {ant: ""}; last_index = 1
        for i, arg in enumerate(args):
            if arg in cmd.options:
                if arg in parts or arg == ant:
                    msg = f"El comando '{ant}' esta repetido"
                    raise CmdLineError(_help=(not self.printed), msg=msg)
                parts[ant] = args[last_index:i]
                last_index = i + 1
                ant = arg       
        parts[ant] = args[last_index:]
        return parts
      
    def _check_opt_restrictions(self, cmd:Command, parts:dict):
        # Comprobamos si puede haber mas de una opcion y si es
        # obligatorio que haya al menos una
        option_names = ""
        for opt in cmd.options.values():
            option_names += opt.name + ", "
        if len(parts) <= 1 and cmd.mandatory_opt: 
            err = (f"El comando '{cmd.name}' requiere una opcion " + 
                f"extra '{option_names[:-2]}'")
            raise CmdLineError(_help=(not self.printed), msg=err)
        elif len(parts) > 2 and not cmd.multi_opt:
            err = (f"El comando '{cmd.name}' solo admite una " +
                f"opcion extra entre '{option_names[:-2]}'")
            raise CmdLineError(_help=(not self.printed), msg=err)
          
      
    def _check_command(self, cmd:Command, params:list) -> list:
        """Revisa si los parametro que se han pasado a un comando 
        (puede ser una opcion de un comando) son validos o si no se 
        le han pasado parametros y el comando los requeria.
        

        Args:
            cmd (Command): Comando a procesar
            params (list): parametros que se le han pasado al comando

        Raises:
            CmdLineError: Si los parametros no son validos para el
                comando

        Returns:
            list: lista con los parametros del comando procesados. Si 
                se han proporcionado numeros en los parametros los 
                devuelve como int y no como str
        """
        if len(params) > 0:
            if len(params) > 1 and not cmd.multi: 
                err_msg = ("No se permite mas de 1 opcion extra " +
                          f"en el comando '{cmd.name}'. Comandos " +
                          f"incorrectos -> {params[1:]}")
                raise CmdLineError(_help=(not self.printed), msg=err_msg)
            if cmd.extra_arg:
                extra_args = []
                for extra in params:
                    try:
                        extra_args.append(int(extra))
                    except:
                        extra_args.append(extra)
                if cmd.choices == None:
                    return extra_args
                # Todos los extra args deben estar en choices
                for extra in extra_args:
                    if extra not in cmd.choices:
                        break
                # Si completa el bucle es que todos son validos
                else:
                    return extra_args
                err_msg = f"El parametro extra '{params[0]}' no es valido"
                raise CmdLineError(_help=(not self.printed), msg=err_msg)
            else:
                err_msg = (f"El comando '{cmd.name}' no admite " + 
                                            f"parametros extra {params}")
                raise CmdLineError(_help=(not self.printed), msg=err_msg)
        elif not cmd.default == None:
            return [cmd.default]
        elif not cmd.mandatory:
            return []
        else:
            err_msg = f"El comando '{cmd.name}' requiere un parametro extra"
            raise CmdLineError(_help=(not self.printed), msg=err_msg)
    
    def _check_flags(self, cmd:Command, args:list) -> list:
        """Revisa que los flags que se han proporcionado son 
        compatibles entre si

        Args:
            args (list): Linea de comandos a procesar

        Raises:
            CmdLineError: Si los comandos no son compatibles

        Returns:
            list: lista con los flags que habia en la linea de 
                de comandos proporcionada (args)
        """  
        if "-h" in args: 
            self.print_help(command=cmd)
            if self.pass_on_help:
                raise HelpException()
            args.remove("-h")
        inFlags = []
        for arg in args: 
            for validFlag in cmd.flags.values():
                if arg == validFlag.name:
                    if len(inFlags) > 0:
                        # Comprobamos que son flags compatibles
                        for flag in inFlags:
                            if (flag.name in validFlag.ncwf or 
                                        validFlag.name in flag.ncwf):
                                errmsg = (f"Los flags '{flag}' y " + 
                                         f"'{validFlag}' no son compatibles")
                                raise CmdLineError(
                                    _help=(not self.printed), msg=errmsg
                                )
                    inFlags.append(validFlag)
        # Eliminamos los flags ya procesadas de la linea de comandos  
        for flag in inFlags: args.remove(flag.name)
        # Guardamos los nombres de los flags en vez del objeto Flag
        # entero (ya no nos hace falta)
        inFlags = list(map(lambda flag: str(flag), inFlags))
        return inFlags
    
    def _check_global_flags(self, args:list):
        inFlags = []
        for arg in args: 
            for validFlag in self.global_flags.values():
                if arg == validFlag.name:
                    if len(inFlags) > 0:
                        # Comprobamos que son flags compatibles
                        for flag in inFlags:
                            if (flag.name in validFlag.ncwf or 
                                        validFlag.name in flag.ncwf):
                                errmsg = (f"Los flags globales '{flag}' y " + 
                                         f"'{validFlag}' no son compatibles")
                                raise CmdLineError(
                                    _help=(not self.printed), msg=errmsg
                                )
                    inFlags.append(validFlag)
      
    def print_help(self, command=None):
        """Imprime las descripciones de cada comando y flag de la cli
        de forma estructurada"""
        self.printed = True
        # ------------------ Parametros a modificar ------------------
        maxline_length = 100; cmd_indent = 4; opt_indent = 12
        cmd_first_line_diff = 10; opt_first_line_diff = 10
        # -------------------- FUNCIONES INTERNAS --------------------
        def apply_shellformat(string:str, indent:int=4):
            return format_str(
                string, 
                maxline_length=maxline_length, 
                indent=indent, 
                tripleq_mode=True
            ) 
            
        def untab_firstline(string:str, indent:int):
            untabbed = ""
            index = string.find("\n")
            if index != -1:
                untabbed += string[:index] + "\n"
                if index < len(string) -1:
                    rest = string[index+1:]
                    untabbed += apply_shellformat(rest, indent=indent)
            else:
                untabbed = string
            return untabbed 
        
        def paint(line:str, color):
            return color + line + colors.ENDC
            
        def print_recursively(cmd:Command, i:int):
            cmd_options = cmd.options.values()
            extra_indent = (opt_indent-cmd_indent)*i
            opt_color = colors.OKCYAN
            if i%2 != 0:
                opt_color = colors.OKBLUE
            if len(cmd_options) > 0:
                print(
                    " "*8*(i+1) + "- " + 
                    paint("options", colors.UNDERLINE) + ":"
                )
                for opt in cmd_options:
                    description = (
                        "=> " + paint(f"'{opt.name}' ", opt_color)
                    )
                    if opt.description is not None:
                        description += f"--> {opt.description}"
                    formatted = apply_shellformat(
                        description, 
                        indent=opt_indent + extra_indent
                    )
                    formatted = untab_firstline(
                        formatted, 
                        indent=opt_indent+opt_first_line_diff + extra_indent
                    )
                    print(formatted)
                    print_recursively(opt, i+1)
            cmd_flags = cmd.flags.values()
            if len(cmd_flags) > 0:
                print(
                    " "*8*(i+1) + "- " +
                    paint("flags", colors.UNDERLINE) + ":"
                )
                for flag in cmd_flags:
                    description = (
                        "=> " + paint(f"'{flag.name}' ", colors.OKGREEN)
                    )
                    if flag.description is not None:
                        description += f"--> {flag.description}"
                    formatted = apply_shellformat(
                        description, 
                        indent=opt_indent + extra_indent
                    )
                    formatted = untab_firstline(
                        formatted, 
                        indent=opt_indent+opt_first_line_diff + extra_indent
                    )
                    print(formatted)
                    
        # ------------------------------------------------------------ 
        commands = self.commands.values()
        if command is not None:
            commands = [command]
        print(paint(" python3 __main__ <gflags> [command] <parameters> " + 
              "<flags> [options] <parameters> <flags> ...", colors.BOLD))
        print(" + " + paint("Commands", colors.UNDERLINE) + ":")
        for cmd in commands:
            description = "    -> " + paint(f"'{cmd.name}' ", colors.WARNING)
            if cmd.description is not None:
                description += f"--> {cmd.description}"
            formatted = apply_shellformat(
                description, indent=cmd_indent
            )
            formatted = untab_firstline(
                formatted, indent=cmd_indent+cmd_first_line_diff
            )
            print(formatted)
            print_recursively(cmd, 0)
        if command is None:
            print(" + " + paint("Global Flags", colors.UNDERLINE) + ":")   
            for flag in self.global_flags.values():
                description = f"    -> '{flag.name}' "
                if flag.description is not None:
                    description += f"--> {flag.description}"
                formatted = apply_shellformat(
                    description, indent=cmd_indent
                )
                formatted = untab_firstline(
                    formatted, indent=cmd_indent+cmd_first_line_diff
                )
                print(formatted)

# -------------------------------------------------------------------- 
class CmdLineError(Exception):
    """Excepcion personalizada para los errores de la cli"""
    def __init__(self, msg:str=None, _help:bool=True):
        if msg is not None:
            hlpm = "\nIntroduce el parametro -h para acceder a la ayuda"
            if _help: 
                msg += hlpm
            super().__init__(msg)
        else:
            super().__init__()
# --------------------------------------------------------------------
class HelpException(Exception):
    pass
# --------------------------------------------------------------------
class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'