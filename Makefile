build:
	docker build -t datawookie/medusa-proxy .

run:
	docker run --rm \
		--name medusa-proxy \
		-e TORS=3 \
		-e HEADS=2 \
		-p 8888:8888 -p 8889:8889 \
		-p 1080:1080 -p 1081:1081 \
		datawookie/medusa-proxy
