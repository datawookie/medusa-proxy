IMAGE = medusa-proxy
VERSION = 0.4.2
USERNAME = datawookie
IMAGE_VERSION = $(USERNAME)/$(IMAGE):$(VERSION)
IMAGE_LATEST = $(USERNAME)/$(IMAGE):latest
PLATFORMS = linux/amd64,linux/arm64
BUILDER = medusa-proxy-multiarch

.PHONY: builder build push run clean

builder:
	@docker buildx inspect $(BUILDER) >/dev/null 2>&1 || docker buildx create --name $(BUILDER) --driver docker-container
	@docker buildx inspect $(BUILDER) --bootstrap >/dev/null

build: builder
	docker buildx build --builder $(BUILDER) --progress=plain --platform $(PLATFORMS) --output type=cacheonly -t $(IMAGE_VERSION) -t $(IMAGE_LATEST) .
	docker buildx build --builder $(BUILDER) --progress=plain --platform local --load -t $(IMAGE_VERSION) -t $(IMAGE_LATEST) .

push: builder
	docker login
	docker buildx build --builder $(BUILDER) --progress=plain --platform $(PLATFORMS) --push -t $(IMAGE_VERSION) -t $(IMAGE_LATEST) .

run:
	@docker stop $(IMAGE) || true
	docker run --rm -it \
		--name $(IMAGE) \
		-e TORS=3 \
		-e HEADS=4 \
		-p 8800:8800 \
		-p 8888:8888 -p 8889:8889 \
		-p 1080:1080 -p 1081:1081 \
		-p 2090:2090 -p 2091:2091 \
		$(IMAGE_VERSION)

clean:
	-@docker rmi -f $(IMAGE_VERSION) $(IMAGE_LATEST) 2>/dev/null
	-@docker builder prune -af
