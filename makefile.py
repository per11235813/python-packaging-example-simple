import sys
from itertools import chain
from pathlib import Path
from utils.makefileutils import run, rm, exec_make
import os

venv_name = "venv"
wheels_dir  =  r"\\md-man.biz\project-cph\bwcph\wheelhouse_3_10"

def venv():
    """Create or update venv"""

    if not Path(venv_name).exists():
        run(f"{sys.executable} -m venv {venv_name}", venv=None)
        if "PIP_INDEX_URL" in os.environ:
            run("pip install pip-tools")

    if "PIP_INDEX_URL" in os.environ:
        run(f"python -m pip install -U pip")
        run("pip freeze > tmp-requirements.old.txt")
        run("pip-compile --no-annotate --no-emit-index-url -o tmp-requirements.dev.txt --extra dev pyproject.toml requirements.in")
        run("pip-sync tmp-requirements.dev.txt")

    else: 
        pip_ini = Path(venv_name) / "pip.ini"
        pip_ini.write_text(f"[install]\nno-index = true\nfind-links = {wheels_dir}")

        run(f"python -m pip install -U pip")
        run(f"python -m pip install -e .[dev]")



def build():
    """Re-build wheel"""
    # setuptools isolation if there is not index
    isolated = "" if "PIP_INDEX_URL" in os.environ else "--no-isolation"
    run(f"python -m build --wheel {isolated}")


def pytest():
    """Run the tests"""
    run("pytest")


def clean():
    """Cleanup build artifacts"""
    rm("dist")
    rm("build")


def clean_all():
    """Cleanup build artifacts and venv"""
    clean()
    rm("venv")


actions = {
    "venv": venv,
    "build": build,
    "pytest": pytest,
    "clean": clean,
    "clean-all": clean_all,
}

if __name__ == "__main__":
    exec_make(actions)
