.. _bmo-changelog:

==========
Change Log
==========

This document records the main changes to the BMO code.

.. _changelog-0.1.0:
0.1.0 (unreleased)
------------------

This is the first release of BMO so this list includes only the most notable features to date.

Added
^^^^^
* Base actor based on `twistedActor <https://github.com/ApachePointObservatory/twistedActor>`_ and TCC device.
* Basic camera control for Allied Vision Manta devices, with camera auto-discovery.
* Display of camera images using DS9 and XPA.
* Command parser based on `click <http://click.pocoo.org/5/>`_. Help commands are broadcasted as responses to the user.
* Basic set of camera control commands (``expose``, ``exptime``, ``reconnect``).
* Loaded cart auto-detection and finding chart display.
* Centroid detection based on `PyGuide <https://github.com/r-owen/PyGuide>`_.
* Centre-up in translation (RA/Dec) and rotation.
* Image background subtraction using `photutils <https://github.com/astropy/photutils>`_.
* Basic astrometry for images.
* Sphinx documentation. Uses `sphinx-click <https://github.com/click-contrib/sphinx-click>`_ to auto-generate available commands.


.. x.y.z (unreleased)
.. ------------------
..
.. A short description
..
.. Added
.. ^^^^^
.. * TBD
..
.. Changed
.. ^^^^^^^
.. * TBD
..
.. Fixed
.. ^^^^^
.. * TBD
