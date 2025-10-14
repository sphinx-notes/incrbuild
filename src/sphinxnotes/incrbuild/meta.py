# This file is generated from sphinx-notes/cookiecutter.
# DO NOT EDIT!!!

################################################################################
# Project meta infos.
################################################################################

from __future__ import annotations
from importlib import metadata

__project__ = 'sphinxnotes-incrbuild'
__author__ = 'Shengyu Zhang'
__desc__ = 'Make sure incremental build available in CI/CD environment'

try:
    __version__ = metadata.version('sphinxnotes-incrbuild')
except metadata.PackageNotFoundError:
    __version__ = 'unknown'
