build:
	docker build -t datawookie/medusa-proxy .

run:
	-docker stop medusa-proxy
	docker run --rm \
		--name medusa-proxy \
		-e TORS=3 \
		-e HEADS=2 \
		-p 8800:8800 \
		-p 8888:8888 -p 8889:8889 \
		-p 1080:1080 -p 1081:1081 \
		-p 2090:2090 -p 2091:2091 \
		datawookie/medusa-proxy
