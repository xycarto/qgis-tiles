-include .creds

BASEIMAGE := qgis-cog-tiler
IMAGE := $(BASEIMAGE):2023-04-13

RUN ?= docker run -it --rm  \
	-e POSTGRES_HOST_AUTH_METHOD=trust \
	-e DISPLAY=$$DISPLAY \
	--env-file .creds \
	-e RUN= -v$$(pwd):/work \
	-w /work $(IMAGE)

# Make tiler docker
cog:	
	$(RUN) bash utils/render-cog.sh "qgis/full-nz-mono"

tiler-edit: Dockerfile
	docker run -it --rm  \
	-e POSTGRES_HOST_AUTH_METHOD=trust \
	-e DISPLAY=$$DISPLAY \
	--env-file .creds \
	-e RUN= -v$$(pwd):/work \
	-w /work $(IMAGE)
	bash
	
tiler-local: Dockerfile
	docker build --tag $(BASEIMAGE) - < $<  && \
	docker tag $(BASEIMAGE) $(IMAGE)

