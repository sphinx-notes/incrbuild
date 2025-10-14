"""
sphinxnotes.incrbuild.utils
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Utils functions.

:copyright: Copyright 2025 Shengyu Zhang
:license: BSD, see LICENSE for details.
"""

import sys
import subprocess
from datetime import datetime
from pathlib import Path
import shutil

from colorama import Fore, Style
from pypi_simple import PyPISimple

from . import meta


def info(text, context=meta.__project__):
    print(f'{Fore.GREEN}[{context}]{Style.RESET_ALL} {text}', file=sys.stderr)


def warn(text, context=meta.__project__):
    print(f'{Fore.YELLOW}[{context}]{Style.RESET_ALL} {text}', file=sys.stderr)


def error(text, context=meta.__project__):
    print(f'{Fore.RED}[{context}]{Style.RESET_ALL} {text}', file=sys.stderr)


def get_pypi_package_release_time(name: str, version: str) -> datetime | None:
    # TODO: cache project page
    with PyPISimple() as client:
        try:
            page = client.get_project_page(name)
        except Exception as e:
            error(f'Failed to get project page of {name}: {e}')
            return None

        pkg = next(p for p in page.packages if p.version == version)
        if pkg is None:
            error(f'Failed to get {name}=={version}: not found')
            return None

        # FIXME: upload_time is always empty
        if pkg.upload_time is None:
            error(f'Failed to get upload time {name}=={version}: None')
            return None

        return pkg.upload_time


def reslove_git_dir(cwd: Path) -> Path:
    cmd = ['git', 'rev-parse', '--show-toplevel']
    try:
        root = subprocess.check_output(cmd, cwd=cwd).strip().decode('utf-8')
    except subprocess.CalledProcessError as e:
        print(f'{cmd} exited with exit code: {e.returncode}')
        raise
    else:
        return Path(root).resolve()


def copy(src: Path, dst: Path):
    info(f'Copying {src} -> {dst}')
    try:
        shutil.copytree(src, dst)
    except FileNotFoundError as e:
        warn(f'Failed to copy files: {e}')


def move(src: Path, dst: Path):
    info(f'Moving {src} -> {dst}')
    try:
        shutil.move(src, dst)
    except FileNotFoundError as e:
        warn(f'Failed to move files: {e}')
