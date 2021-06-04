
from .apps_cmd.apps import get_apps_cmd
from dependencies.cli.aux_classes import Command, Flag, Option


# --------------------------------------------------------------------
def get_repo_cmd():
    msg = """allows to interact with the local repositories"""
    repo = Command(
        "repo", description=msg,
        mandatory_opt=True
    )
    # ++++++++++++++++++++++++++++
    apps = get_apps_cmd()
    repo.add_option(apps)
    
    return repo

# --------------------------------------------------------------------
# --------------------------------------------------------------------