# -*- coding: utf-8 -*-
# Planet CRS Registry - The coordinates reference system registry for solar bodies
# Copyright (C) 2021-2024 - CNES (Jean-Christophe Malapert for PDSSP)
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
import os

import toml

project_root = os.path.dirname(os.path.dirname(__file__))
pyproject_path = os.path.join(project_root, "pyproject.toml")

# Charger les métadonnées depuis pyproject.toml
with open(pyproject_path, "r") as file:
    pyproject_content = toml.load(file)

project_tool = pyproject_content.get("tool", {})
project_metadata = project_tool.get("poetry", {})

__name_soft__ = project_metadata.get("name", "unknown")
__version__ = project_metadata.get("version", "0.0.0")
__title__ = project_metadata.get("name", "unknown")
__description__ = project_metadata.get("description", "")
__url__ = project_metadata.get("homepage", "")
__author__ = project_metadata.get("authors", [{}])[0]
__author_email__ = project_metadata.get("authors", [{}])[0]
__license__ = project_metadata.get("license", "")
__copyright__ = "2021-2024, CNES (Jean-Christophe Malapert for PDSSP)"
