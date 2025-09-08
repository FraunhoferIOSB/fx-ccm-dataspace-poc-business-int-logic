#!/bin/sh
set -eu
exec java -jar starter.jar --config /app/config/server_config.json
