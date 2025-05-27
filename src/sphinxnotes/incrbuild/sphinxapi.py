"""
sphinxnotes.incrbuild.main
~~~~~~~~~~~~~~~~~~~~~~~~~~

Sphinx-related code.

:copyright: Copyright 2025 Shengyu Zhang
:license: BSD, see LICENSE for details.
"""

from os import path
import argparse
import site

# There aren't public APIs, but there aren't many better options
from sphinx.config import Config, eval_config_file
from sphinx.cmd.build import get_parser as sphinx_get_parser


def get_html_theme_dir(conf: str) -> str:
    cfg = eval_config_file(conf, None)
    theme = cfg.get('html_theme', 'alabaster')
    theme_dir = path.join(*site.getsitepackages(), theme)
    return theme_dir


def get_build_parser(injection):
    # NOTE:
    # sphinx.cmd.build.get_parser is not considered to be public API,
    # but as this is a first-party project, we can cheat a little bit.
    parser = sphinx_get_parser()
    for action in parser._actions:
        if hasattr(action, "version"):
            # Fix the version
            action.version = f"%(prog)s 0.0.1"
            break
    parser.add_argument(
        "-M",
        dest="use_make_mode",
        help=argparse.SUPPRESS,
    )

    injection(parser)

    return parser
