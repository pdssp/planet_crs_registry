#!/bin/sh
# Planet CRS Registry - The coordinates reference system registry for solar bodies
# Copyright (C) 2021 - CNES (Jean-Christophe Malapert for Pôle Surfaces Planétaires)
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

search=`docker images | grep dev/planet_crs_registry | wc -l`
if [ $search = 0 ];
then
	# only the heaader - no image found
	echo "Please build the image by running 'make docker-container-dev'"
	exit 1
fi

ps=`docker ps -a | grep develop-planet_crs_registry | wc -l`
if [ $ps = 0 ];
then
	echo "no container available, start one"
	docker run --name=develop-planet_crs_registry #\
		#-v /dev:/dev \
		#-v `echo ~`:/home/${USER} \
		#-v `pwd`/data:/srv/planet_crs_registry/data \
		#-p 8082:8082 \
		-it dev/planet_crs_registry /bin/bash
	exit $?
fi

ps=`docker ps | grep develop-planet_crs_registry | wc -l`
if [ $ps = 0 ];
then
	echo "container available but not started, start and go inside"
	docker start develop-planet_crs_registry
	docker exec -it develop-planet_crs_registry /bin/bash
else
	echo "container started, go inside"
	docker exec -it develop-planet_crs_registry /bin/bash
fi
