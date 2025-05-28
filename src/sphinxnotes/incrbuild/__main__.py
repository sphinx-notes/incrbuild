"""
sphinxnotes.incrbuild.main
~~~~~~~~~~~~~~~~~~~~~~~~~~

sphinxnotes-incrbuild CLI entry entrypoint.

:copyright: Copyright 2025 Shengyu Zhang
:license: BSD, see LICENSE for details.

Copied from https://github.com/sphinx-doc/sphinx-autobuild/blob/main/sphinx_autobuild/__main__.py
"""

from __future__ import annotations

import argparse
import sys
import os
import time
from pathlib import Path
import subprocess
from importlib import metadata 
import site
from datetime import datetime

from colorama import Fore, Style
from pypi_simple import PyPISimple

from . import sphinxapi

__PROG__ = 'sphinxnotes-incrbuild'
# __VERSION__ = metadata.version('sphinxnotes.incrbuild')
__VERSION__ = '0.1.0'

def main(argv=()):
    """Actual application logic."""

    if not argv:
        # entry point functions don't receive args
        argv = sys.argv[1:]
    args, build_args = _parse_args(list(argv))

    info(f'Running {__PROG__} {__VERSION__}, cache will be stored in {args.cache}')

    if args.builder in ['html']:
        theme = sphinxapi.get_html_theme(args.confdir or args.srcdir)
        info(f'Current theme: {theme}')
        restore_theme_files_mtime(theme)

        git_dir = reslove_git_dir(args.srcdir)
        info(f'Git root: {git_dir}')
        restore_git_files_mtime(git_dir)
    else:
        info(f'Only HTML builder is supported, nothing todo')

    info(f'Running sphinx-build {' '.join(build_args)}...')
    sphinxapi.run(build_args)


def _parse_args(argv):
    # Parse once with the Sphinx parser to emit errors
    # and capture the ``-d`` and ``-w`` options.
    sphinx_args = sphinxapi.get_build_parser(_inject_parser).parse_args(argv.copy())

    # Parse a second time with just our parser
    parser = argparse.ArgumentParser(allow_abbrev=False)
    _inject_parser(parser)
    args, build_args = parser.parse_known_args(argv.copy())

    # Copy needed settings
    args.srcdir = Path(sphinx_args.sourcedir).resolve(strict=True)
    args.outdir = Path(sphinx_args.outputdir).resolve()
    args.confdir = Path(sphinx_args.confdir).resolve() if sphinx_args.confdir else None
    args.doctreedir = (
        Path(sphinx_args.doctreedir).resolve() if sphinx_args.doctreedir else None
    )
    args.builder = sphinx_args.builder or sphinx_args.use_make_mode or ''
    args.make_mode = sphinx_args.use_make_mode is not None

    return args, build_args


def _inject_parser(parser: argparse.ArgumentParser):
    parser.description = None
    parser.epilog = None
    parser.prog = __PROG__

    version_hooked = False
    for action in parser._actions:
        if hasattr(action, 'version'):
            # Fix the version
            action.version = f'%(prog)s {__VERSION__}'
            version_hooked = True
            break
    if not version_hooked:
        parser.add_argument(
            '--version', action='version', version=f'%(prog)s {__VERSION__}'
        )

    group = parser.add_argument_group('incrbuild options')
    group.add_argument(
        '--cache',
        type=str,
        default=f'/tmp/{__PROG__}',
        help='path to directory that will be cached by CI/CD',
    )

    return parser


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
        __import__('pprint').pprint(pkg)
        if pkg.upload_time is None:
            error(f'Failed to get upload time {name}=={version}: None')
            return None
        return pkg.upload_time


def restore_theme_files_mtime(theme: str):
    """
    Sphinx HTML builder will rebuild the whole project when **modification time
    (mtime) of templates of theme** newer than built result [1]_.
    
    These theme templates vendored in pip packages are newly installed,
    so their mtime always newr than the built result.
    Set mtime to 1990 to make sure the project won't rebuilt.
    
    .. [1] https://github.com/sphinx-doc/sphinx/blob/847ad0c991e21db9daa02fec09acbd456f353300/sphinx/builders/html/__init__.py#L371
    """
    theme_dir = Path(*site.getsitepackages()).resolve().joinpath(theme)
    theme_version = metadata.version(theme)
    theme_mtime = get_pypi_package_release_time(theme, theme_version)
    if theme_mtime is None:
        theme_mtime = datetime.fromtimestamp(190001010000)
    info(f'Release time of {theme}=={theme_version}: {theme_mtime}')
    theme_html_files = list(
        Path(root, sfile)
        for root, _dirs, files in os.walk(theme_dir)
        for sfile in files
        if sfile.endswith('.html')
    )
    for html_file in theme_html_files:
        old_mtime = html_file.stat().st_mtime
        info(f'Restoring mtime of {html_file.name}: {datetime.fromtimestamp(old_mtime)} -> {theme_mtime}') # TODO: debug?
        try:
            os.utime(html_file, (time.time(), theme_mtime.timestamp()), follow_symlinks=True)
        except PermissionError as e:
            error(f'Failed to set mtime of file {html_file.name}: {e}')
        sys.exit(-1)


def reslove_git_dir(cwd: Path) -> Path:
    cmd = ["git", "rev-parse", "--show-toplevel"]
    try:
        root = subprocess.check_output(cmd, cwd=cwd).strip().decode('utf-8')
    except subprocess.CalledProcessError as e:
        print(f'{cmd} exited with exit code: {e.returncode}')
        raise
    else:
        return Path(root).resolve()


def restore_git_files_mtime(git_dir: Path):
    # See ``[tool.setuptools.package-data]`` section of pyproject.toml to know
    # how gittools are included.
    prefix = Path(__file__).parent.resolve()
    git_restore_mtime = prefix.joinpath('gittools', 'git-restore-mtime')

    cmd = [git_restore_mtime]
    p = subprocess.Popen(cmd, stderr=subprocess.PIPE, cwd=git_dir)
    for line in p.stderr or []:
        line = line.decode('utf-8').strip()
        info(f'{Fore.BLUE}[git-restore-mtime]{Style.RESET_ALL} {line}')
    p.wait()
    if p.returncode != 0:
        error(f'{cmd} exited with exit code: {p.returncode}')
        sys.exit(p.returncode)


def info(text):
    print(f"{Fore.GREEN}[{__PROG__}]{Style.RESET_ALL} {text}")


def error(text):
    print(f"{Fore.RED}[{__PROG__}]{Style.RESET_ALL} {text}")


if __name__ == '__main__':
    main(sys.argv[1:])
