
from contextlib import suppress

import dependencies.lxc.lxc as lxc
from program.platform import platform
from dependencies.utils.tools import  remove_many


# --------------------------------------------------------------------
global_image = None; checked = False
def _check_global_image(options:dict, flags:list):
    global global_image, checked
    if not checked:
        image = None
        if "--image" in options:
            image = _check_image(options["--image"][0], flags)
        global_image = image
        checked = True
    return global_image
    
def get_servers_opts(options:dict, flags:list):
    simage = _check_global_image(options, flags); names = []
    if "--simage" in options:
        simage = _check_image(options["--simage"][0], flags)
    if "--name" in options:   
        names = options["--name"]
    return simage, names

def get_lb_opts(options:dict, flags:list):
    lbimage = _check_global_image(options, flags)
    algorithm = None; port = None
    if "--lbimage" in options:
        lbimage = _check_image(options["--lbimage"][0], flags)
    if "--balance" in options:
        algorithm = options["--balance"][0]
    if "--port" in options:
        port = options["--port"][0]
    return lbimage, algorithm, port

def get_cl_opts(options:dict, flags:list):
    climage = _check_global_image(options, flags); clname = "cl"
    if "--climage" in options:
        climage = _check_image(options["--climage"][0], flags)
    with suppress(Exception):
        clname = options["--client"][0]
    return climage, clname

def get_db_opts(options:dict,flags:list):
    dbimage = _check_global_image(options, flags)
    if "--dbimage" in options:
        dbimage = _check_image(options["--dbimage"][0], flags)
    return dbimage

def _check_image(image:str, flags:list):
    if "-y" not in flags:
        im_list = lxc.lxc_image_list()
        fingerprints = im_list.keys()
        aliases = []
        for f in fingerprints:
            aliases.append(im_list[f]["ALIAS"])
        if image not in fingerprints and image not in aliases:
            print(f"La imagen '{image}' no se encuentra en el " +
                "repositorio local de aplicaciones")
            answer = input("¿Utilizar de todos modos?(y/n): ")
            if answer.lower() != "y":
                return None
    return image

def check_skip_opt(args:list, options:dict):
    if "--skip" in options:
        cs_names_to_skip = options["--skip"]
        arg_names = list(map(str, args))
        remove_many(arg_names, *cs_names_to_skip)
        args = platform.search_cs(*arg_names)
    return args

def get_cs(args:list, options:dict, tags=[]):
    talk = True; skip = []
    if len(args) == 0:
        talk = False
    if "--skip" in options:
        skip = options["--skip"]
    cs = platform.search_cs(args, tags=tags, skip=skip, talk=talk)
    return cs