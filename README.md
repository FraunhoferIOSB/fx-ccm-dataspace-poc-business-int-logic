# 


## generate docker images first:

cd Data-Source
docker build -t data-source-image --file Data-Source.Dockerfile .
cd ..


## modify paths in docker-compose.yaml

## start container with compose
docker compose up -d