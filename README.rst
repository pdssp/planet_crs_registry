.. highlight:: shell

===============================
Planet CRS Registry
===============================

.. image:: https://img.shields.io/github/v/tag/pdssp/planet_crs_registry
.. image:: https://img.shields.io/github/v/release/pdssp/planet_crs_registry?include_prereleases

.. image https://img.shields.io/github/downloads/pdssp/planet_crs_registry/total
.. image https://img.shields.io/github/issues-raw/pdssp/planet_crs_registry
.. image https://img.shields.io/github/issues-pr-raw/pdssp/planet_crs_registry
.. image:: https://img.shields.io/badge/Maintained%3F-yes-green.svg
   :target: https://github.com/pdssp/planet_crs_registry/graphs/commit-activity
.. image https://img.shields.io/github/license/pdssp/planet_crs_registry
.. image https://img.shields.io/github/forks/pdssp/planet_crs_registry?style=social


The coordinates reference system registry for solar bodies



Stable release
--------------

To install Planet CRS Registry, run this command in your terminal:

.. code-block:: console

    $ pip install planet_crs_registry

This is the preferred method to install Planet CRS Registry, as it will always install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/



From sources (without virtual environment)
------------

The sources for Planet CRS Registry can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/pdssp/planet_crs_registry

Or download the `tarball`_:

.. code-block:: console

    $ curl -OJL https://github.com/pdssp/planet_crs_registry/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ make  # install in the system root
    $ make user # or Install for non-root usage


.. _Github repo: https://github.com/pdssp/planet_crs_registry
.. _tarball: https://github.com/pdssp/planet_crs_registry/tarball/master



From sources (with virtual environment)
------------

The sources for Planet CRS Registry can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/pdssp/planet_crs_registry

Or download the `tarball`_:

.. code-block:: console

    $ curl -OJL https://github.com/pdssp/planet_crs_registry/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ make prepare-dev
    $ source .planet_crs_registry # Use the virtual environment
    $ make


.. _Github repo: https://github.com/pdssp/planet_crs_registry
.. _tarball: https://github.com/pdssp/planet_crs_registry/tarball/master



Development
-----------

.. code-block:: console

        $ git clone https://github.com/pdssp/planet_crs_registry
        $ cd planet_crs_registry
        $ make prepare-dev
        $ source .planet_crs_registry
        $ make install-dev


To get more information about the preconfigured tasks:

.. code-block:: console

        $ make help



Usage
-----

To use Planet CRS Registry in a project::

    planet_crs_registry



Docker
------

.. code-block:: console

        $ docker pull pdssp/planetary-crs-registry # get the image

### Run the registry as Http

.. code-block:: console

        $ docker run -p 8080:8080 mizarweb/planetary-crs-registry

### Run the registry as Https

Create the SSL certificate

.. code-block:: console

        $ mkdir -p /tmp/conf
        $ cd /tmp/conf
        $ mkcert -cert-file cert.pem -key-file key.pem 0.0.0.0 localhost 127.0.0.1 ::1

Edit the configuration file

.. code-block:: console

        $ vi /tmp/conf/planet_crs_registry.conf

And set the configuration file as follows:

```
[HTTPS]
host = 0.0.0.0
port = 5000
ssl_keyfile = key.pem
ssl_certfile = cert.pem
```
Create the container

.. code-block:: console

        $ docker run --name=pdssp-planet_crs_registry -p 5000:5000 -v /tmp/conf:/conf pdssp/planet_crs_registry


     ### Run the registry as both Http and Https

Create the SSL certificate

.. code-block:: console

        $ mkdir -p /tmp/conf
        $ cd /tmp/conf
        $ mkcert -cert-file cert.pem -key-file key.pem 0.0.0.0 localhost 127.0.0.1 ::1

Edit the configuration file

.. code-block:: console

        $ vi /tmp/conf/planet_crs_registry.conf

And set the configuration file as follows:

```
[HTTP]
host = 0.0.0.0
port = 8080

[HTTPS]
host = 0.0.0.0
port = 5000
ssl_keyfile = key.pem
ssl_certfile = cert.pem
```
Create the container

.. code-block:: console

        $ docker run --name=pdssp-planet_crs_registry -p 5000:5000 -p 8080:8080 -v /tmp/conf:/conf pdssp/planet_crs_registry


### Stop the registry

.. code-block:: console

        $ docker stop pdssp-planet_crs_registry


### Restart the registry

.. code-block:: console

        $ docker start pdssp-planet_crs_registry


Run tests
---------

.. code-block:: console

        $make tests


Author
------
👤 **Jean-Christophe Malapert**



🤝 Contributing
---------------
Contributions, issues and feature requests are welcome!<br />Feel free to check [issues page](https://github.com/pole-surfaces-planetaires/planet_crs_registry/issues). You can also take a look at the [contributing guide](https://github.com/pole-surfaces-planetaires/planet_crs_registry/blob/master/CONTRIBUTING.rst)


📝 License
----------
This project is [GNU Lesser General Public License v3](https://github.com/pole-surfaces-planetaires/planet_crs_registry/blob/master/LICENSE) licensed.
