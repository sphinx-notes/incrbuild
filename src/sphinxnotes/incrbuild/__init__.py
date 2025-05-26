"""
sphinxnotes.incrbuild
~~~~~~~~~~~~~~~~~~~~~

:copyright: Copyright 2025 Shengyu Zhang
:license: BSD, see LICENSE for details.
"""

import time
import os
from os import path
from pathlib import Path
import subprocess

# Sphinx HTML builder will rebuild the whole project when **modification time
# (mtime) of templates of theme** newer than built result [1]_.
#
# These theme templates vendored in pip packages are newly installed,
# so their mtime always newr than the built result.
# Set mtime to 1990 to make sure the project won't rebuilt.
#
# .. [1] https://github.com/sphinx-doc/sphinx/blob/847ad0c991e21db9daa02fec09acbd456f353300/sphinx/builders/html/__init__.py#L371

def set_mtime(fn, mtime: float):
    atime = time.time()
    os.utime(fn, (atime, mtime), follow_symlinks=True)

def restore_theme_files_mtime(theme: str):
    # TODO
    new_mtime = 190001010000
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


def restore_git_files_mtime(git_dir: str):
    # See ``[tool.setuptools.package-data]`` section of pyproject.toml to know
    # how git-tools are included.
    prefix = path.abspath(path.dirname(__file__))
    git_restore_mtime = path.join(prefix, 'git_tools', 'git-restore-mtime')

    try:
        subprocess.run([git_restore_mtime], check=True, cwd=git_dir)
    except subprocess.CalledProcessError as e:
        print(f"git-restore-mtime exited with exit code: {e.returncode}")

