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
from pathlib import Path

# This isn't public API, but there aren't many better options
from sphinx.cmd.build import get_parser as sphinx_get_parser

from . import sphinxapi

__version__ = '0.1.0'

def main(argv=()):
    """Actual application logic."""

    if not argv:
        # entry point functions don't receive args
        argv = sys.argv[1:]
    args, build_args = _parse_args(list(argv))
    print(f'args: {args}')
    print(f'build_args: {build_args}')


def _parse_args(argv):
    # Parse once with the Sphinx parser to emit errors
    # and capture the ``-d`` and ``-w`` options.
    sphinx_args = sphinxapi.get_build_parser(_inject_parser).parse_args(argv.copy())

    # Parse a second time with just our parser
    parser = argparse.ArgumentParser(allow_abbrev=False)
    _inject_parser(parser)
    args, build_args = parser.parse_known_args(argv.copy())

    # Copy needed settings
    args.sourcedir = Path(sphinx_args.sourcedir).resolve(strict=True)
    args.outdir = Path(sphinx_args.outputdir).resolve()
    if sphinx_args.doctreedir:
        args.doctree_dir = Path(sphinx_args.doctreedir).resolve()
    else:
        args.doctree_dir = None
    if sphinx_args.warnfile:
        args.warnings_file = Path(sphinx_args.warnfile).resolve()
    else:
        args.warnings_file = None

    # Copy the make-mode builder, if present
    args.make_mode_builder = sphinx_args.use_make_mode or ""

    return args, build_args


def _inject_parser(parser: argparse.ArgumentParser):
    parser.description = None
    parser.epilog = None
    parser.prog = "sphinx-incrbuild"

    version_hooked = False
    for action in parser._actions:
        if hasattr(action, "version"):
            # Fix the version
            action.version = f"%(prog)s 0.0.1"
            version_hooked = True
            break
    if not version_hooked:
        parser.add_argument(
            "--version", action="version", version=f"sphinx-incrbuild {__version__}"
        )

    group = parser.add_argument_group("incrbuild options")
    group.add_argument(
        "--port",
        type=int,
        default=8000,
        help="port to serve documentation on. 0 means find and use a free port",
    )

    return parser


if __name__ == "__main__":
    main(sys.argv[1:])
