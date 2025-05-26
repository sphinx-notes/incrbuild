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

.. INTRODUCTION END

Getting Started
===============

.. note::

   We assume you already have a Sphinx documentation,
   if not, see `Getting Started with Sphinx`_.

First, downloading extension from PyPI:

.. code-block:: console

   $ pip install sphinxnotes-incrbuild

Then, add the extension name to ``extensions`` configuration item in your
:parsed_literal:`conf.py_`:

.. code-block:: python

   extensions = [
             # …
             'sphinxnotes.incrbuild',
             # …
             ]

.. _Getting Started with Sphinx: https://www.sphinx-doc.org/en/master/usage/quickstart.html
.. _conf.py: https://www.sphinx-doc.org/en/master/usage/configuration.html

.. ADDITIONAL CONTENT START

.. ADDITIONAL CONTENT END

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
