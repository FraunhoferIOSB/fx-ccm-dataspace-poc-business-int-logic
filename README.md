# How to Deploy the container


## generate docker images first:

cd Data-Source
docker build -t data-source-image  .
cd ..

cd OPCUA-Server
docker build -t opcua-server-image .
cd ..

## modify paths in docker-compose.yaml
last line with "device:"

## start container with compose
docker compose up -d

# Internal reminder
WICHTIG:
Der FreeOPCUA Server hat ein Bug, dass die Currenttime im Status nicht aktualisiert wird, deswegen muss sich einmalig auf den Docker verbunden werden und das Patch kopiert werden:
(base) ziermto@gargamel:~$ docker exec -it MX-Adapter-OPCUA-Server /bin/bash
root@32ebd45e95a9:/usr/app/src# cp internal_server.py.mod /usr/local/lib/python3.11/site-packages/asyncua/server/internal_server.py