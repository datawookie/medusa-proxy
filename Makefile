IMAGE = medusa-proxy
VERSION = 0.3.0
USERNAME = datawookie
IMAGE_VERSION = $(USERNAME)/$(IMAGE):$(VERSION)
IMAGE_LATEST = $(USERNAME)/$(IMAGE):latest

build:
	echo $(IMAGE_VERSION)
	docker build --progress=plain -t $(IMAGE_VERSION) -t $(IMAGE_LATEST) .

push:
	docker login
	docker push $(IMAGE_VERSION)
	docker push $(IMAGE_LATEST)

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
