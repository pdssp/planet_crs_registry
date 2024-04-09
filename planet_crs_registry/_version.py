# -*- coding: utf-8 -*-
# Planet CRS Registry - The coordinates reference system registry for solar bodies
# Copyright (C) 2021-2022 - CNES (Jean-Christophe Malapert for PDSSP)
#
# This file is part of Planet CRS Registry.
#
# Planet CRS Registry is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License v3  as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Planet CRS Registry is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License v3  for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Planet CRS Registry.  If not, see <https://www.gnu.org/licenses/>.
"""Project metadata."""
from pkg_resources import DistributionNotFound
from pkg_resources import get_distribution

__name_soft__ = "planet_crs_registry"
try:
    __version__ = get_distribution(__name_soft__).version
except DistributionNotFound:
    __version__ = "0.0.0"
__title__ = "Planet CRS Registry"
__description__ = "The coordinates reference system registry for solar bodies"
__url__ = "https://github.com/pole-surfaces-planetaires/planet_crs_registry"
__author__ = "Jean-Christophe Malapert"
__author_email__ = "jean-christophe.malapert@cnes.fr"
__license__ = "GNU Lesser General Public License v3"
__copyright__ = "2021-2022, CNES (Jean-Christophe Malapert for PDSSP)"
