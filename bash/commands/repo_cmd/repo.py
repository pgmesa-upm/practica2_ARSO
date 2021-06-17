
# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from .apps_cmd.apps import get_apps_cmd, apps

# --------------------------------------------------------------------
def get_repo_cmd():
    msg = """allows to interact with the local repositories"""
    repo = Command(
        "repo", description=msg,
        mandatory_nested_cmd=True
    )
    # ++++++++++++++++++++++++++++
    apps = get_apps_cmd()
    repo.nest_cmd(apps)
    
    return repo

# --------------------------------------------------------------------
# --------------------------------------------------------------------
def repo(args:list=[], options:dict={}, flags:list=[], nested_cmd:dict={}):
    if "apps" in nested_cmd:
        cmd_info = nested_cmd.pop("apps")
        apps(**cmd_info)