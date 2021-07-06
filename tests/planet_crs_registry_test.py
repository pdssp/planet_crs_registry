# -*- coding: utf-8 -*-
import pytest

import planet_crs_registry
import logging


def test_name():
    name = planet_crs_registry.__name_soft__
    assert name == "planet_crs_registry"


def test_logger():
    loggers = [logging.getLogger()]
    loggers = loggers + [
        logging.getLogger(name) for name in logging.root.manager.loggerDict
    ]
    assert loggers[0].name == "root"
    assert loggers[1].name == "planet_crs_registry"
