===============
Getting Started
===============

.. currentmodule:: ultimo

At the moment installation is from the GitHub repo source.  In the future
we would like to add ``mip`` and better stub file support.

Installation
------------

Ultimo can be installed from github via :py:mod:`mip`.  For most use-cases
you will probably want to install :py:mod:`ultimo_machine` which will also
insatll the core :py:mod:`ultimo` package:

..  code-block:: python-console

    >>> mip.install("github:unital/ultimo/src/ultimo_machine/package.json")

or using :py:mod:`mpremote`:

..  code-block:: console

    mpremote mip install github:unital/ultimo/src/ultimo_machine/package.json

You can separately install :py:mod:`ultimo_display` from
``github:unital/ultimo/src/ultimo_display/package.json`` and if you just
want the core :py:mod:`ultimo` without any hardware support, you can install
``github:unital/ultimo/src/ultimo/package.json``.

Development Installation
------------------------

To simplify the development work-cycle with actual hardware, there is a
helper script in the ci directory which will download the files onto the
device.  You will need an environment with ``mpremote`` and ``click``
installed.  For example, on a Mac/Linux machine:

..  code-block:: console

    python -m venv ultimo-env
    source ultimo-env/bin/activate
    pip install mpremote click

should give you a working environment.

Ensure that the Pico is plugged in to your computer and no other program
(such as Thonny or an IDE) is using it.  You can then execute:

..  code-block:: console

    python -m ci.deploy_to_device

and this will install the ultimo code in the ``/lib`` directory (which is
on :py:obj:`sys.path`) and the examples in the main directory (with
example drivers in ``/devices``).

Running the Examples
--------------------

The example code works with the Pico and it's internal hardware, plus some
basic external hardware (buttons, potentiometers, motion sensors).  A couple
of examples use a Waveshare LCD1602 RGB or similar I2C-based 16x2 character
displays.

Most examples can be run from inside an IDE like Thonny.  A couple need better
serial console support than Thonny provides, and so may need to use
``mpremote``, ``screen`` or other terminal emulators.

..  warning::

    As of the initial release, the examples have only been run on a Raspberry
    Pi Pico.  They *probably* will work on other supported hardware with
    appropriate modification for pin locations, etc.

Writing Code Using Ultimo
-------------------------

Althought Ultimo is a Micropython library, it provides ``.pyi`` stub files for
typing support.  If you add the ultimo sources to the paths where tools like
``mypy`` and ``pyright`` look for stubs (in particular, ``pip install -e ...``
will likely work), then you should be able to get type-hints for the code you
are writing in your IDE or as a check step as part of your CI.
