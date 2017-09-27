.. _bmo-changelog:

==========
Change Log
==========

This document records the main changes to the BMO code.


.. _changelog-0.2.0:

0.2.0 (unreleased)
------------------

Added
^^^^^
* BMO now provides a full logging system which also catches Twisted messages.
* A fake Vimba controller which provides at least some basic functionality like connecting a camera.
* Outputs actorkeys keywords for camera devices, exposure state, and controller.
* Finding charts are now, by default, grabbed from platelist.
* Acquisition camera positions on the plates are grabbed from the DB.
* Partially filled up documentation on how to use BMO.

Changed
^^^^^^^
* Exposing the cameras is now asynchronous. Both cameras can be exposed at the same time without blocking.
* Background estimation now only happens for the first image in the series. For any subsequent image, the first background is subtracted. If the exposure time changes, the background is recalculated.
* ``bmo ds9 clear`` is now an alias to ``bmo ds9 reset``.

Fixed
^^^^^
* Thanks to the asynchronous exposing, the problem with TCC status timing out during centring up should now be fixed.


.. _changelog-0.1.0:

0.1.0 (2017-09-15)
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
