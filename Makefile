build:
	docker build -t tor-proxy-rotating .

run:
	docker run --rm --name tor-proxy-rotating -p 8888:8888 -p 1080:1080 tor-proxy-rotating
