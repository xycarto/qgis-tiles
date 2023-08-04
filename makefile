-include .creds

BASEIMAGE := xycarto/qgis-tiler
IMAGE := $(BASEIMAGE):2023-04-22

RUN ?= docker run -it --rm  \
	--user=$$(id -u):$$(id -g) \
	-e DISPLAY=$$DISPLAY \
	--env-file .creds \
	-e RUN= -v $$(pwd):/work \
	-w /work $(IMAGE)

PHONEY: index raster-tiles

cog:	
	$(RUN) bash utils/render-cog.sh "qgis/full-nz-mono"

# make index matrix=NZTM2000 zoom=1
index:
	$(RUN) python3 utils/raster-tiling/idx-matrix.py $(matrix) $(zoom)

# make raster-tiles matrix=NZTM2000 zoom=0 qgis=qgis/full-nz-mono.qgz
raster-tiles:	
	$(RUN) python3 utils/raster-tiling/render-zoom.py $(matrix) $(zoom) $(qgis)

raster-tiles-test:	
	$(RUN) python3 utils/raster-tiling/raster-tiler-test-grid.py "qgis/full-nz-mono.qgz"

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