.. _bmo-how:

How to use BMO
==============

Basic usage
-----------

There are many ways in which BMO can be used, depending on the particular circumstances, but the basic procedure is as follows:

1. Make sure that DS9 is :ref:`properly connected <bmo-how-ds9>`.

2. When a new cart gets loaded, BMO should identify it and automatically load the finding charts for the new plate. If that does not happen, run ``bmo ds9 show_chart``. You can add a plate id to the `previous command <api.html#bmo-ds9-show-chart>`__ to specify a plate.

3. Start exposing by running ``bmo camera expose``. You can use the modifier ``--camera_type`` to indicate that you only want to expose the on-axis camera (``on``) or the off axis one (``off``). You can change the exposure time with ``bmo camera exptime <time>``. You can use the flag ``--camera_time`` for that command as well.

4. You should see the stars in DS9, as well as some green circles indicating where the code things the centroid of the stars are.

5. If BMO is identifying the centroids of the stars correctly, you can issue ``bmo centre_up`` to offset the telescope and centre the field. You can pass it the ``-t`` flag to offset only in translation, not in rotation.

6. If BMO fails to identify the right star, but you can still see it, stop the exposures with ``bmo camera stop``. Then, manually, move the green circles on each DS9 frame until they are on top of the correct star, and as centred on the centroid of the star as possible. Now run ``bmo centre_up``. BMO will use your manually modified centroids.


.. _bmo-how-ds9:

How to connect DS9 to BMO
-------------------------

Normally, when you restart BMO, it should automatically connect to the instance of DS9 you are running. However, in some cases that may not be the case. This section deals with how to set up the DS9 XPA system from scratch. It deals with the case of BMO at LCO, but it can be easily generalised. XPA is a messaging system used to communicate with different pieces of software, including DS9. It allows, among other things, to display data obtained in one computer (in our case sdss4-hub, where BMO is running) on a DS9 instance running on a different computer (snafu).

Unfortunately, the documentation around XPA is less than clear, an it uses a very custom system. Some documentation can be found `here <http://www.astro.louisville.edu/software/sbig/archive/xmccd-4.1/xmccd-4.1e/docs/xpa/xpa.pdf>`_, with some more details on communication between hosts `here <https://hea-www.harvard.edu/RD/xpa/inet.html>`_.

First, make sure that `XPA <https://github.com/ericmandel/xpa>`_ and `DS9 <http://ds9.si.edu/site/Home.html>`_ are installed both in snafu and sdss4-hub. Use the Mac version for the former and the Linux version for the latter. Make sure that `pyds9 <https://github.com/ericmandel/pyds9>`_ is also installed in both computers.

Now we want to make sure that snafu accepts connections from sdss4-hub and that it uses the correct ports. In the home directory in snafu we create a file called ``acls.xpa`` with the content ``DS9:ds9 10.1.1.20 +``. This tells XPA in snafu that connections from 10.1.1.20 (sdss4-hub) are accepted.

XPA uses two ports. We fix them by creating a file in snafu called ``~/ports.xpa`` and adding to it ``DS9:ds9 4096 4097``. Now we close all instances of DS9 in snafu and open a new one. If we do ``File -> XPA -> Information`` we should see that the ``XPA_METHOD`` is a string that ends in 4096. The first part of the string is the unique identifier for that DS9 instance.

To test that it works, log in to sdss4-hub, open a Python terminal and run

.. code-block:: python

    import pyds9
    dd = pyds9.DS9('snafu:4096')
    dd.set('frame new')

If a new frame pops up in DS9 everything should be ready.


How to get help
---------------

All the commands you can use with BMO are listed in the :ref:`bmo-api` section. Ultimately, BMO's parser is a standard CLI (in particular we use `click <http://click.pocoo.org/>`_) so the syntax should be quite natural to anybody used to Unix systems.

In particular, it is possible to use the ``--help`` flag anywhere to obtain help about a particular command. In STUI, to obtain general information about the available commands do ``bmo help``. You will get a list of messages in STUI composing describing the commands. Now, if you want information about the subcommands to control the cameras, do ``bmo camera --help``. If you want to know what flags and options are available for the ``expose`` command, do ``bmo camera expose --help``.

This works with all the commands!
