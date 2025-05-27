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

from . import sphinxapi


def main(argv=()):
    """Actual application logic."""

    if not argv:
        # entry point functions don't receive args
        argv = sys.argv[1:]
    args, build_args = _parse_args(list(argv))

    print(f'args: {args}')
    print(f'build_args: {build_args}')

    theme_dir = sphinxapi.get_html_theme_dir(args.confdir or args.srcdir)
    print(f'theme_dir: {theme_dir}')
    # restore_theme_files_mtime(theme_dir)

    git_dir = reslove_git_dir(args.srcdir)
    print(f'git_dir: {git_dir}')
    restore_git_files_mtime(git_dir)

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
    parser.prog = 'sphinx-incrbuild'

    version = metadata.version('sphinxnotes.incrbuild')
    version = '0.0.1'
    version_hooked = False
    for action in parser._actions:
        if hasattr(action, 'version'):
            # Fix the version
            action.version = f'%(prog)s {version}'
            version_hooked = True
            break
    if not version_hooked:
        parser.add_argument(
            '--version', action='version', version=f'sphinx-incrbuild {version}'
        )

    group = parser.add_argument_group('incrbuild options')
    group.add_argument(
        '--build-cache',
        action='store_true',
        help='print path of data that needs to be cached by CI/CD',
    )

    return parser


def restore_theme_files_mtime(theme_dir: Path):
    """
    Sphinx HTML builder will rebuild the whole project when **modification time
    (mtime) of templates of theme** newer than built result [1]_.
    
    These theme templates vendored in pip packages are newly installed,
    so their mtime always newr than the built result.
    Set mtime to 1990 to make sure the project won't rebuilt.
    
    .. [1] https://github.com/sphinx-doc/sphinx/blob/847ad0c991e21db9daa02fec09acbd456f353300/sphinx/builders/html/__init__.py#L371
    """

    new_mtime = 190001010000 # TODO: read template release time
    theme_html_files = list(
        Path(root, sfile)
        for root, _dirs, files in os.walk(theme_dir)
        for sfile in files
        if sfile.endswith('.html')
    )
    for html_file in theme_html_files:
        old_mtime = html_file.stat().st_mtime
        print(f'Fixing mtime of {html_file.name}: {old_mtime} -> {new_mtime}')
        atime = time.time()
        os.utime(html_file, (atime, new_mtime), follow_symlinks=True)



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
    try:
        subprocess.run(cmd, check=True, cwd=git_dir)
    except subprocess.CalledProcessError as e:
        print(f'{cmd} exited with exit code: {e.returncode}')
        raise



if __name__ == '__main__':
    main(sys.argv[1:])
