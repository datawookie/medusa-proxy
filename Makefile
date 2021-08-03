build:
	docker build -t tor-proxy-rotating .

run:
	docker run --rm --name tor-proxy-rotating -e NTOR=3 -e NPRIVOXY=2 \
		-p 8888:8888 -p 8889:8889 \
		-p 1080:1080 -p 1081:1081 \
		tor-proxy-rotating
