#!/bin/sh
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
# You should have received a copy of the GNU Lesser General Public License v3
# along with Planet CRS Registry.  If not, see <https://www.gnu.org/licenses/>.
set search
set ps

search=`docker images | grep pdssp/planet_crs_registry | wc -l`
if [ $search = 0 ];
then
	# only the heaader - no image found
	echo "Please build the image by running 'make docker-build'"
	exit 1
fi

ps=`docker ps -a | grep pdssp-planet_crs_registry | wc -l`
if [ $ps = 0 ];
then
	echo "no container available, start one"
	docker run --name=pdssp-planet_crs_registry \
	-p 8080:8080 -p 5000:5000 \
	pdssp/planet_crs_registry
	exit $?
fi

ps=`docker ps | grep pdssp-planet_crs_registry | wc -l`
if [ $ps = 0 ];
then
	echo "container available but not started, start it"
	docker start pdssp-planet_crs_registry
else
	echo "container already started"
fi
