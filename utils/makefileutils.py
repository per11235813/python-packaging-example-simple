from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from subprocess import PIPE, CalledProcessError, Popen


def run(
    cmd: str, echo_cmd=True, echo_stdout=True, cwd: Path | None = None, venv: str | None = "venv", env=None, ignore_errors=False
) -> str:
    """Run shell command with option to print stdout incrementally
    If venv is set, the command will be run in the virtual environment"""

    if venv is not None and "-m venv" in cmd and not Path(venv).exists():
        msg = "You try to create a virtual environment using a virtual environment, that does not exists. Set venv=None"
        print(msg, file=sys.stderr)
        sys.exit(1)
    elif venv is not None:
        activate_relative = rf".\{venv}\Scripts\activate.bat" if os.name == "nt" else f"./{venv}/bin/activate"
        activate = f"{Path(activate_relative).absolute()}"

        cmd = f'"{activate}" && {cmd}'

        if not Path(activate).exists():
            print(f"{venv} - {activate} - is not a virtual environment", file=sys.stderr)
            sys.exit(1)

    if echo_cmd:
        print(f"##\n## Running: {cmd}", end="")
    if cwd:
        print(f"\n## cwd: {cwd}")
    if echo_cmd:
        print(f"\n")

    res = []
    proc = Popen(cmd, stdout=PIPE, stderr=sys.stderr, shell=True, text=True, cwd=cwd, env=env)
    while proc.poll() is None:
        if proc.stdout is None:
            continue

        line = proc.stdout.readline()
        res.append(line)
        if echo_stdout:
            print(line, end="", flush=True)

    if proc.returncode != 0 and not ignore_errors:
        raise CalledProcessError(proc.returncode, cmd)

    return "".join(res)


def rm(path: Path | str, echo_cmd: bool = True):
    """Remove file or folder"""
    path = Path(path) if isinstance(path, str) else path
    if echo_cmd:
        print(f"## Removing: {path}")
    if path.is_file():
        path.unlink()
    elif path.is_dir():
        try:
            shutil.rmtree(path)
        except PermissionError as e:
            print(f"Failed to remove {path}, error: {e}")


def check_git(version_prefix="v") -> tuple[str, str, str]:
    run("git fetch")
    git_status = run("git status", echo_stdout=False)
    git_clean = "working tree clean" in git_status and "Your branch is up to date with 'origin/" in git_status
    if not git_clean:
        print("Git index is dirty. Exiting ...", file=sys.stderr)
        sys.exit(1)

    version, name = get_pyproject_data()
    git_tag = f"{version_prefix}{version}"

    if git_tag in run("git tag -l"):
        msg = f"Git tag: {git_tag} is already used. Update version in pyproject.toml. Exiting ..."
        print(msg, file=sys.stderr)
        sys.exit(1)

    return name, version, git_tag


def get_pyproject_data(pyproject_toml: Path = Path("pyproject.toml")) -> tuple[str, str]:
    import tomli

    pyproject_toml_data = tomli.loads(pyproject_toml.read_text(encoding="utf8"))
    version = pyproject_toml_data["project"]["version"]
    package_name = pyproject_toml_data["project"]["name"]

    return version, package_name


def exec_make(actions):
    """Execute makefile actions"""
    cmd = sys.argv[0]
    sub_cmd = sys.argv[1] if len(sys.argv) == 2 else None

    if sub_cmd in actions and sub_cmd:
        actions[sub_cmd]()
    else:
        print(f"Options for '{sys.executable} {cmd}':")
        for arg, func in actions.items():
            doc_str = func.__doc__.split("\n")[0] if func.__doc__ else ""
            print(f"   {arg: <18}{doc_str}")
        sys.exit(1)


def get_url_from_git_config(conf: Path = Path.cwd() / ".git" / "config") -> str:
    """Get the url from the git config file"""
    lines = conf.read_text().splitlines()
    urls = [line.split(" = ")[1].strip() for line in lines if line.startswith("\turl = ")]
    assert len(urls) == 1, "More than one url found in git config"

    return urls[0]


def str_to_clipboard(s, msg: str | None = None):
    import win32clipboard

    win32clipboard.OpenClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, s)
    win32clipboard.CloseClipboard()
    if msg:
        print(msg)
