.. This file is generated from sphinx-notes/cookiecutter.
   You need to consider modifying the TEMPLATE or modifying THIS FILE.

=====================
sphinxnotes-incrbuild
=====================

.. |docs| image:: https://img.shields.io/github/deployments/sphinx-notes/incrbuild/github-pages?label=docs
   :target: https://sphinx.silverrainz.me/incrbuild
   :alt: Documentation Status
.. |license| image:: https://img.shields.io/github/license/sphinx-notes/incrbuild
   :target: https://github.com/sphinx-notes/incrbuild/blob/master/LICENSE
   :alt: Open Source License
.. |pypi| image:: https://img.shields.io/pypi/v/sphinxnotes-incrbuild.svg
   :target: https://pypi.python.org/pypi/sphinxnotes-incrbuild
   :alt: PyPI Package
.. |download| image:: https://img.shields.io/pypi/dm/sphinxnotes-incrbuild
   :target: https://pypi.python.org/pypi/sphinxnotes-incrbuild
   :alt: PyPI Package Downloads
.. |github| image:: https://img.shields.io/badge/GitHub-181717?style=flat&logo=github&logoColor=white/
   :target: https://github.com/sphinx-notes/incrbuild
   :alt: GitHub Repository

|docs| |license| |pypi| |download| |github|

Introduction
============

.. INTRODUCTION START

As we know, Sphinx supports incremental HTML build, and it works well locally.
But for CI/CD, the environment is usually brand new, which causes Sphinx
always to rebuild everything.

The project wraps :parsed_literal:`sphinx-build_` and ensures the environment
is "incremental build" -able before running the real ``sphinx-build``.

.. _sphinx-build: https://www.sphinx-doc.org/en/master/man/sphinx-build.html

.. INTRODUCTION END

Getting Started
===============

.. note::

   For most users, please go directly to `GitHub Actions`_ and `GitLab CI`_.

First, downloading extension from PyPI:

.. code-block:: console

   $ pip install sphinxnotes-incrbuild


.. ADDITIONAL CONTENT START

After installation, command ``sphin-incrbuild`` should be available.
Use need to replace their ``sphinx-build`` command to ``sphin-incrbuild``.

All arguments of ``sphin-incrbuild`` are same to :parsed_literal:`sphinx-build_`
except:

:``--cache CACHE``: path to directory that will be cached by CI/CD

Use should use CI/CD's Cache mechanism, restore cache file to cache directory
pass the directory to ``sphin-incrbuild`` via ``--cache``, and upload the cache
after build finished, in pseudocode:

.. code-block:: yaml

   - run: restore /tmp/cache
   - run: sphinx-incrbuild --cache /tmp/cache <other Sphinx options...>
   - run: upload /tmp/cache

GitHub Actions
--------------

``sphinxnotes-incrbuild`` is already integrated into action `sphinx-notes/pages@v3`__,
just set ``cache: true`` to enable incremental build.

.. code-block:: yaml
   :emphasize-lines: 4

   - id: deployment
     uses: sphinx-notes/pages@v3
     with:
       cache: true

__ https://github.com/marketplace/actions/sphinx-to-github-pages

GitLab CI
---------

TODO

Contents
========

.. toctree::
   :caption: Contents

   changelog

The Sphinx Notes Project
========================

The project is developed by `Shengyu Zhang`__,
as part of **The Sphinx Notes Project**.

.. toctree::
   :caption: The Sphinx Notes Project

   Home <https://sphinx.silverrainz.me/>
   Blog <https://silverrainz.me/blog/category/sphinx.html>
   PyPI <https://pypi.org/search/?q=sphinxnotes>

__ https://github.com/SilverRainZ
