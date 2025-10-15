"""
sphinxnotes.incrbuild.main
~~~~~~~~~~~~~~~~~~~~~~~~~~

sphinxnotes-incrbuild CLI entry entrypoint.

:copyright: Copyright 2025 Shengyu Zhang
:license: BSD, see LICENSE for details.

"""

from __future__ import annotations

import argparse
import sys
import os
import time
from pathlib import Path
import subprocess
from importlib import metadata
from datetime import datetime
import shutil
from packaging.requirements import Requirement

from . import sphinxapi, meta
from .utils import info, warn, error, reslove_git_dir, copy, move


def main(argv=()) -> int:
    if not argv:
        # entry point functions don't receive args
        argv = sys.argv[1:]
    args, build_args = _parse_args(list(argv))

    info(
        f'Running {meta.__project__} {meta.__version__}, cache directory: {args.cache}'
    )

    if args.builder not in ['html']:
        warn('Only HTML builder is supported, passthrough')
        info(f'Running sphinx-build {" ".join(build_args)}...')
        return sphinxapi.run(build_args)

    cache_dir = Path(args.cache).resolve()
    if args.make_mode:
        html_dir = args.outdir.joinpath('html')
        doctrees_dir = args.doctreedir or args.outdir.joinpath('doctrees')
    else:
        html_dir = args.outdir
        doctrees_dir = args.doctreedir or args.outdir.joinpath('.doctrees')

    restore_cache(cache_dir, html_dir, doctrees_dir)

    theme = sphinxapi.get_html_theme(args.confdir or args.srcdir)
    restore_theme_files_mtime(theme)

    git_dir = reslove_git_dir(args.srcdir)
    restore_git_files_mtime(git_dir)

    info(f'Running sphinx-build {" ".join(build_args)}...')
    returncode = sphinxapi.run(build_args)

    if returncode == 0:
        save_cache(cache_dir, html_dir, doctrees_dir)
    else:
        warn(f'Skip saving cache because Sphinx returns {returncode}')

    return returncode


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
    args.outdir.mkdir(exist_ok=True)  # ensure outdir exists
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
    parser.prog = meta.__project__

    version_hooked = False
    for action in parser._actions:
        if hasattr(action, 'version'):
            # Fix the version
            action.version = f'%(prog)s {meta.__version__}'
            version_hooked = True
            break
    if not version_hooked:
        parser.add_argument(
            '--version', action='version', version=f'%(prog)s {meta.__version__}'
        )

    cache_dir = os.path.join('/tmp', meta.__project__)
    group = parser.add_argument_group('incrbuild options')
    group.add_argument(
        '--cache',
        type=str,
        default=cache_dir,
        help=f'path to directory that will be cached by CI/CD (default: {cache_dir})',
    )

    return parser


def restore_theme_files_mtime(theme: str):
    """
    Sphinx HTML builder will rebuild the whole project when **modification time
    (mtime) of templates of theme** newer than built result [1]_.

    These theme templates vendored in pip packages are newly installed,
    so their mtime always newr than the built result.
    Set mtime to 1990 to make sure the project won't rebuilt.

    .. [1] https://github.com/sphinx-doc/sphinx/blob/847ad0c991e21db9daa02fec09acbd456f353300/sphinx/builders/html/__init__.py#L371
    """
    info(f'Current theme: {theme}')

    HTML_FILE_MTIME = datetime(1900, 1, 1)

    # Find all HTML files of theme and its dependencies.
    # For example: sphinx_book_theme depends on pydata-sphinx-theme.
    deps = [theme, 'sphinx']
    for dep in metadata.requires(theme) or []:
        req = Requirement(dep)
        if req.marker is not None:
            continue  # skip optional dependencies
    html_files = []
    for dep in deps:
        for file in metadata.files(dep) or []:
            if file.suffix != '.html':
                continue
            html_files.append(file.locate())

    for html_file in html_files:
        old_mtime = html_file.stat().st_mtime
        info(
            f'Restoring mtime of {html_file.name}: {datetime.fromtimestamp(old_mtime)} -> {HTML_FILE_MTIME}'
        )  # TODO: debug?
        try:
            os.utime(
                html_file,
                (time.time(), HTML_FILE_MTIME.timestamp()),
                follow_symlinks=True,
            )
        except PermissionError as e:
            error(f'Failed to set mtime of file {html_file.name}: {e}')
            sys.exit(-1)


def restore_git_files_mtime(git_dir: Path):
    info(f'Git root: {git_dir}')

    # See ``[tool.setuptools.package-data]`` section of pyproject.toml to know
    # how gittools are included.
    prefix = Path(__file__).parent.resolve()
    git_restore_mtime = prefix.joinpath('git-tools', 'git-restore-mtime')

    cmd = [git_restore_mtime]
    p = subprocess.Popen(cmd, stderr=subprocess.PIPE, cwd=git_dir)
    for line in p.stderr or []:
        line = line.decode('utf-8').rstrip()
        info(line, context='git-restore-mtime')
    p.wait()
    if p.returncode != 0:
        error(f'{cmd} exited with exit code: {p.returncode}')
        sys.exit(p.returncode)


def restore_cache(cache_dir: Path, html_dir: Path, doctree_dir: Path):
    info(f'Restoring cache from {cache_dir}...')

    if not cache_dir.exists():
        warn(f"Cache directory {cache_dir} doesn't exist")
        return
    shutil.rmtree(html_dir, ignore_errors=True)
    shutil.rmtree(doctree_dir, ignore_errors=True)

    # Move may be faster than copy.
    move(cache_dir.joinpath('html'), html_dir)
    move(cache_dir.joinpath('doctrees'), doctree_dir)


def save_cache(cache_dir: Path, html_dir: Path, doctree_dir: Path):
    info(f'Saving cache to {cache_dir}...')

    # Clear cache dir.
    shutil.rmtree(cache_dir, ignore_errors=True)
    cache_dir.mkdir()

    # Move may be faster than copy.
    # NOTE: Copy html_dir here, it is also used as artifacts.
    copy(html_dir, cache_dir.joinpath('html'))
    move(doctree_dir, cache_dir.joinpath('doctrees'))


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
