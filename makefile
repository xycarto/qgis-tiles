-include .creds

BASEIMAGE := xycarto/qgis-tiler
IMAGE := $(BASEIMAGE):2023-04-22

RUN ?= docker run -it --rm  \
	--user=$$(id -u):$$(id -g) \
	-e DISPLAY=$$DISPLAY \
	--env-file .creds \
	-e RUN= -v $$(pwd):/work \
	-w /work $(IMAGE)

PHONEY: index raster-tiles coverage gebco

##### PROCESS DATA #####

gebco:
	$(RUN) bash utils/webmer-data/gebco-clean.sh

##### MAKE TILES #####
cog:	
	$(RUN) bash utils/render-cog.sh "qgis/full-nz-mono"

# time make coverage epsg=2193 qgis="qgis/full-nz-mono.qgz" minzoom=10 maxzoom=11 version=v1
coverage:
	$(RUN) bash utils/raster-tiling/coverage.sh $(epsg) $(qgis) $(minzoom) $(maxzoom) $(version)

# make index matrix=NZTM2000 zoom=1
index:
	$(RUN) python3 utils/raster-tiling/idx-matrix.py $(matrix) $(zoom)

# make no-index matrix=NZTM2000 zoom=0 qgis=qgis/full-nz-mono.qgz coverage="data/coverage/full-nz.gpkg" version="v1"
no-index:
	$(RUN) python3 utils/raster-tiling/test-start-point.py  $(matrix) $(zoom) $(qgis) $(coverage) $(version)

# make raster-tiles matrix=NZTM2000 zoom=0 qgis=qgis/full-nz-mono.qgz coverage="data/coverage/full-nz.gpkg"
raster-tiles:	
	$(RUN) python3 utils/raster-tiling/render-zoom.py $(matrix) $(zoom) $(qgis) $(coverage)

# make raster-tiles-test matrix=NZTM2000 zoom=0 qgis=qgis/full-nz-mono.qgz coverage="data/coverage/full-nz.gpkg"
raster-tiles-test:	
	$(RUN) python3 utils/raster-tiling/render-zoom-no-index.py $(matrix) $(zoom) $(qgis) $(coverage)

test-local: Dockerfile
	docker run -it --rm  \
	--user=$$(id -u):$$(id -g) \
	-e DISPLAY=$$DISPLAY \
	--env-file .creds \
	-e RUN= -v$$(pwd):/work \
	-w /work $(IMAGE)
	bash
	
tiler-local: Dockerfile
	docker build --tag $(BASEIMAGE) - < $<  && \
	docker tag $(BASEIMAGE) $(IMAGE)

tiler-push: Dockerfile
	echo $(DOCKER_PW) | docker login --username xycarto --password-stdin
	docker build --tag $(BASEIMAGE) - < $<  && \
	docker tag $(BASEIMAGE) $(IMAGE) && \
	docker push $(IMAGE)

tiler-pull:
	docker pull $(IMAGE)