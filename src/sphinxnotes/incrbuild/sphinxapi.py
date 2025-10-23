"""
sphinxnotes.incrbuild.main
~~~~~~~~~~~~~~~~~~~~~~~~~~

Sphinx-related code.

:copyright: Copyright 2025 Shengyu Zhang
:license: BSD, see LICENSE for details.
"""

import argparse
from pathlib import Path

# NOTE: There aren't public APIs, but there aren't many better options
from sphinx.config import eval_config_file
from sphinx.errors import ConfigError
from sphinx.cmd.build import get_parser, main


from .utils import error


def get_html_theme(conf_dir: Path) -> str:
    DEFAULT_HTML_THEME = 'alabaster'
    try:
        cfg = eval_config_file(conf_dir.joinpath('conf.py'), None)
    except ConfigError as e:
        error(f'Failed to get html theme from config file {conf_dir}: {e}')
        return DEFAULT_HTML_THEME
    else:
        return cfg.get('html_theme', DEFAULT_HTML_THEME)


def get_build_parser(injection):
    parser = get_parser()
    parser.add_argument(  # fix the hidden -M flag.
        '-M',
        dest='use_make_mode',
        help=argparse.SUPPRESS,
    )
    injection(parser)
    return parser


def run(args: list[str]) -> int:
    return main(args)
