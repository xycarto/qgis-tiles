-include .creds

BASEIMAGE := xycarto/qgis-tiler
IMAGE := $(BASEIMAGE):2023-08-24

BASEIMAGE_TERRAFORM := xycarto/terraform
IMAGE_TERRAFORM := $(BASEIMAGE):2023-10-05

RUN ?= docker run -it --rm  \
	--user=$$(id -u):$$(id -g) \
	-e DISPLAY=$$DISPLAY \
	--env-file .creds \
	-e RUN= -v $$(pwd):/work \
	-w /work $(IMAGE)

RUN_TERRAFORM ?= docker run -it --rm  \
	--user=$$(id -u):$$(id -g) \
	-e DISPLAY=$$DISPLAY \
	--env-file .creds \
	-e RUN= -v $$(pwd):/work \
	-w /work $(IMAGE_TERRAFORM)

PHONEY: 

##### MAKE TILES #####
# time make coverage epsg=2193 qgis="qgis/full-nz-mono.qgz" minzoom=10 maxzoom=11 version=v1
# time make coverage epsg=3857 qgis="qgis/world-webmer.qgz" minzoom=0 maxzoom=2 version=v1
coverage:
	$(RUN) bash utils/raster-tiling/coverage.sh $(epsg) $(qgis) $(minzoom) $(maxzoom) $(version)

raster-tiles:
	$(RUN) python3 utils/raster-tiling/raster-tiler.py  $(matrix) $(zoom) $(qgis) $(coverage) $(version) $(cores)

terraform:
	$(RUN_TERRAFORM) bash terraform-configs/build-infra.sh
	

##### DOCKER #####
test-local: docker/Dockerfile
	docker run -it --rm  \
	--user=$$(id -u):$$(id -g) \
	-e DISPLAY=$$DISPLAY \
	--env-file .creds \
	-e RUN= -v$$(pwd):/work \
	-w /work $(IMAGE)
	bash
	
docker-local: docker/Dockerfile
	docker build --tag $(BASEIMAGE) - < docker/Dockerfile  && \
	docker tag $(BASEIMAGE) $(IMAGE)

docker-push: docker/Dockerfile
	echo $(DOCKER_PW) | docker login --username xycarto --password-stdin
	docker build --tag $(BASEIMAGE) - < docker/Dockerfile  && \
	docker tag $(BASEIMAGE) $(IMAGE) && \
	docker push $(IMAGE)

docker-pull:
	echo $(DOCKER_PW) | docker login --username xycarto --password-stdin
	docker pull $(IMAGE)

##### DOCKER TERRAFORM #####
docker-local-terraform: docker/Dockerfile.terraform
	docker build --tag $(BASEIMAGE_TERRAFORM) - < docker/Dockerfile.terraform && \
	docker tag $(BASEIMAGE_TERRAFORM) $(IMAGE_TERRAFORM)

docker-push-terraform: Dockerfile.terraform
	echo $(DOCKER_PW) | docker login --username xycarto --password-stdin
	docker build --tag $(BASEIMAGE_TERRAFORM) - < docker/Dockerfile.terraform && \
	docker tag $(BASEIMAGE_TERRAFORM) $(IMAGE_TERRAFORM) && \
	docker push $(IMAGE_TERRAFORM)

docker-pull-terraform:
	docker pull $(IMAGE_TERRAFORM)