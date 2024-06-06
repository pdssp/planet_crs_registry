=======
Compose
=======

Variants
========

Current compose configuration uses `merge <https://github.com/compose-spec/compose-spec/blob/master/13-merge.md#merge-and-override>`_ capability to provide pluggable functionality:

#. ``compose.yaml`` contains the core functionality: the *planetary-crs-registry* app, based on an in-memory SQLite database.
#. ``observability.yaml`` add a *Grafana* based stack to collect and display telemetry.


Run
===

To launch the *planetary crs registry* alone, do::

$ docker-compose up

To launch the application and monitoring, do::

$ docker-compose -f compose.yaml -f observability.yaml up


Access
======

Services are accessible at the following addresses:

* *planetary crs registry*: http://localhost:8080
* *Grafana dashboards*: http://localhost:3000
* *Grafana Alloy debug UI*: http://localhost:12345


Telemetry
=========


Principles
----------

This compose environment relies on `Open-telemetry <https://opentelemetry.io/>`_ as foundation to collect and send telemetry data from applications to the monitoring platform.

The monitoring platform itself uses `Grafana open-source edition <https://grafana.com/oss/>`_:


.. raw:: html
  :file: ./telemetry.drawio.html

#. First, *planetary crs registry* application is launched with `FastAPI OpenTelemetry instrumentation <https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html>`_ support. It intercepts activity (ASGI calls and log records), and send related information to an OTLP compatible receiver.
#. We use `Grafana Alloy <https://grafana.com/oss/alloy-opentelemetry-collector/>`_ as OpenTelemetry collector, as it allow to perform advanced transformation, like Geolocation of client IP addresses.
#. Once collected and processed, telemetry data is stored in dedicated systems: `Grafana Loki <https://grafana.com/oss/loki/>`_ for log records, and `Grafana Tempo <https://grafana.com/oss/tempo/>`_ for tracing data.
#. Finally, `Grafana <https://grafana.com/oss/grafana/>`_ queries both *Loki* and *Tempo* to create reports.

Geolocation
-----------

By default, geolocation processing is deactivated, because it requires to setup a `MaxMind GeoLite2 database <https://dev.maxmind.com/geoip/geolite2-free-geolocation-data>`_.

To setup the process:

#. Download the database
    #. Create an account (or connect to your account) on `MaxMind website <https://www.maxmind.com/en/account/login>`_
    #. From your account page, select *Download Files* in ``GeoIP2/GeoLite2`` menu (left side).
    #. Download the ``GeoLite2 City`` file in format ``GeoIP2 Binary (.mmdb)``.
    #. Unzip the download file to get the ``.mmdb`` file directly on your system.
#. Activate GeoIP processing
    #. Move/copy the GeoLite2 database to ``./confs/grafana/alloy/`` directory, and name it ``geolite2-city.mmdb``.
    #. Uncomment the ``stage.geoip`` block in `Alloy configuration file <file:./confs/grafana/alloy/config.alloy>`_
#. Restart the compose configuration


Dashboards
----------

The compose configuration ships a simple Grafana dashboard.
To access it, do:

#. Open `Grafana dashboard import window <http://localhost:3000/dashboard/import>`_ in your browser
#. Drag and drop the ``confs/grafana/dashboards/http-accesses.json`` file
#. On the next window, choose default *Loki* and *Tempo* datasources.
#. You should be redirected to the dashboard page.
#. You can perform some requests on *planetary crs registry* (e.g. http://localhost:8080/ws/IAU/2015/1000), to verify the dashboard is filled with new data.
