
# Imports para definicion del comando
from dependencies.cli.aux_classes import Command, Flag, Option
from .apps_cmd.apps import get_apps_cmd

# --------------------------------------------------------------------
def get_repo_cmd():
    msg = """allows to interact with the local repositories"""
    repo = Command(
        "repo", description=msg,
        mandatory_opt=True
    )
    # ++++++++++++++++++++++++++++
    apps = get_apps_cmd()
    repo.nest_cmd(apps)
    
    return repo

# --------------------------------------------------------------------
# --------------------------------------------------------------------
def repo():
    pass