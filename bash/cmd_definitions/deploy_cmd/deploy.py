
from dependencies.cli.aux_classes import Command, Flag, Option
from ..reused_definitions import reused_opts, reused_flags


# --------------------------------------------------------------------
def get_deploy_cmd():
    cmd_name = "deploy"
    msg = """
    <void or integer between(1-5)> --> deploys a server platform with
    the number of servers especified (if void, 2 servers are created).
    It also initializes a load balancer that acts as a bridge between 
    the servers and a data base for storing data. Everything is 
    connected by 2 virtual bridges
    """
    deploy = Command(
        cmd_name, description=msg, 
        extra_arg=True, choices=[1,2,3,4,5], default=2
    )
    # ++++++++++++++++++++++++++++
    name = _def_name_opt()
    deploy.add_option(name)
    # ++++++++++++++++++++++++++++
    client = _def_client_opt()
    deploy.add_option(client)
    # ++++++++++++++++++++++++++++
    balance = _def_balance_opt()
    deploy.add_option(balance)
    # ++++++++++++++++++++++++++++
    image = _def_image_opt()
    deploy.add_option(image)
    # ++++++++++++++++++++++++++++
    simage = _def_simage_opt()
    deploy.add_option(simage)
    # ++++++++++++++++++++++++++++
    lbimage = _def_lbimage_opt()
    deploy.add_option(lbimage)
    # ++++++++++++++++++++++++++++
    dbimage = _def_dbimage_opt()
    deploy.add_option(dbimage)
    # ++++++++++++++++++++++++++++
    climage = _def_climage_opt()
    deploy.add_option(climage)
    # Flags ---------------------- 
    deploy.add_flag(reused_flags["-l"])
    
    return deploy

# --------------------------------------------------------------------
# -------------------------------------------------------------------- 
def _def_name_opt():
    msg = """
    <server_names> allows to specify the names of the servers"""
    name = Option(
        "--name", description=msg,
        extra_arg=True, mandatory=True, multi=True
    )
    return name
def _def_client_opt():
    msg = """ 
    <void or client_name> creates a client connected to the load 
    balancer
    """
    client = Option("--client", description=msg, extra_arg=True)
    return client

def _def_balance_opt():
    msg = """ 
    <algorithm_name> allows to specify the balance algorithm of the
    load balancer (roundrobin, leastconn, source, ...). By default 
    'roundrobin' is used
    """
    balance = Option(
        "--balance", description=msg, 
        extra_arg=True, mandatory=True
    )
    return balance

def _def_image_opt():
    msg = """ 
    <alias or fingerprint> allows to specify the image of the
    containers, by default ubuntu:18.04 is used
    """
    image = Option(
        "--image", description=msg, 
        extra_arg=True, mandatory=True
    )
    return image

def _def_simage_opt():
    msg = """ 
    <alias or fingerprint> allows to specify the image of the 
    servers
    """
    simage = Option(
        "--simage", description=msg, 
        extra_arg=True, mandatory=True
    )
    return simage

def _def_lbimage_opt():
    msg = """ 
    <alias or fingerprint> allows to specify the image of the 
    load balancer
    """
    lbimgae = Option(
        "--lbimage", description=msg, 
        extra_arg=True, mandatory=True
    )
    return lbimgae

def _def_dbimage_opt():
    msg = """ 
    <alias or fingerprint> allows to specify the image of the 
    data base
    """
    dbimage = Option(
        "--dbimage", description=msg, 
        extra_arg=True, mandatory=True
    )
    return dbimage

def _def_climage_opt():
    msg = """ 
    <alias or fingerprint> allows to specify the image of the 
    client
    """
    climage = Option(
        "--climage", description=msg, 
        extra_arg=True, mandatory=True
    )
    return climage
