-include .creds

BASEIMAGE := xycarto/qgis-tiler
IMAGE := $(BASEIMAGE):2023-08-24

RUN ?= docker run -it --rm  \
	--user=$$(id -u):$$(id -g) \
	-e DISPLAY=$$DISPLAY \
	--env-file .creds \
	-e RUN= -v $$(pwd):/work \
	-w /work $(IMAGE)

PHONEY: 

##### MAKE TILES #####
# time make coverage epsg=2193 qgis="qgis/full-nz-mono.qgz" minzoom=10 maxzoom=11 version=v1
# time make coverage epsg=3857 qgis="qgis/world-webmer.qgz" minzoom=0 maxzoom=2 version=v1
coverage:
	$(RUN) bash utils/raster-tiling/coverage.sh $(epsg) $(qgis) $(minzoom) $(maxzoom) $(version)

# make raster-tiles matrix=${MATRIX} zoom=${zoom} qgis=${PROJECT} coverage=${path} version=$VERSION cores=$CORES
raster-tiles:
	$(RUN) python3 utils/raster-tiling/raster-tiler.py  $(matrix) $(zoom) $(qgis) $(coverage) $(version) $(cores)
	

##### DOCKER #####
test-local: Dockerfile
	docker run -it --rm  \
	--user=$$(id -u):$$(id -g) \
	-e DISPLAY=$$DISPLAY \
	--env-file .creds \
	-e RUN= -v$$(pwd):/work \
	-w /work $(IMAGE)
	bash
	
docker-local: Dockerfile
	docker build --tag $(BASEIMAGE) - < $<  && \
	docker tag $(BASEIMAGE) $(IMAGE)

docker-push: Dockerfile
	echo $(DOCKER_PW) | docker login --username xycarto --password-stdin
	docker build --tag $(BASEIMAGE) - < $<  && \
	docker tag $(BASEIMAGE) $(IMAGE) && \
	docker push $(IMAGE)

docker-pull:
	docker pull $(IMAGE)