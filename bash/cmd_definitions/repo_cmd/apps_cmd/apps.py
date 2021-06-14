
from dependencies.cli.aux_classes import Command, Flag, Option
from ...reused_definitions import reused_opts


# --------------------------------------------------------------------
def get_apps_cmd():
    msg = """allows to interact with the apps local repository"""
    apps = Command(
        "apps", description=msg,
        mandatory_opt=True, multi_opt=False
    )
    # ++++++++++++++++++++++++++++
    add  = _def_add_opt()
    apps.add_option(add)
    # ++++++++++++++++++++++++++++
    rm = _def_rm_opt()
    apps.add_option(rm)
    # ++++++++++++++++++++++++++++
    setdef = _def_setdef_opt()
    apps.add_option(setdef)
    # ++++++++++++++++++++++++++++
    unsetdef = _def_unsetdef_opt()
    apps.add_option(unsetdef)
    # ++++++++++++++++++++++++++++
    ls = _def_list_opt()
    apps.add_option(ls)
    # ++++++++++++++++++++++++++++-
    clear = _def_clear_opt()
    apps.add_option(clear)
    
    return apps
    
# --------------------------------------------------------------------
# --------------------------------------------------------------------
def _def_add_opt():
    msg = """
    <absolute_paths> adds 1 or more apps to the local repository
    """
    add = Option(
        "add", description=msg, 
        extra_arg=True, mandatory=True, multi=True
    )
    add.add_option(reused_opts["--name"])
    return add

# --------------------------------------------------------------------
def _def_rm_opt():
    msg = """<app_names> removes apps from the local repository"""
    rm = Option(
        "rm", description=msg, 
        extra_arg=True, mandatory=True, multi=True
    )
    return rm

# --------------------------------------------------------------------
def _def_setdef_opt():
    msg = """
    <app_name> changes the default app of the servers"""
    setdef = Option(
        "setdef", description=msg, 
        extra_arg=True, mandatory=True
    )
    return setdef

# --------------------------------------------------------------------
def _def_unsetdef_opt():
    msg = """makes the default app to be none"""
    unsetdef = Option("unsetdef", description=msg)
    return unsetdef

# --------------------------------------------------------------------
def _def_list_opt():
    ls = Option(
        "list", description="lists the apps of repository"
    )
    return ls

# --------------------------------------------------------------------
def _def_clear_opt():
    clear = Option(
        "clear", description="clears the apps repository"
    )
    return clear
# --------------------------------------------------------------------
