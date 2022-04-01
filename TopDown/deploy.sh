#!/bin/zsh

docker build -t meltcheck:latest .
docker stop tgdeploy
docker rm tgdeploy
docker run --name tgdeploy --network=db-net -d meltcheck