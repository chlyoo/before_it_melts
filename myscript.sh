#!/bin/zsh
docker network create db-net
docker build -t meltcheck:latest .
docker pull mongo
docker run --name db -p 27017:27017 --network=db-net -v ~/data:/data/db -e MONGO_INITDB_ROOT_USERNAME="admin" -e MONGO_INITDB_ROOT_PASSWORD="ckdgusmongodb" -e MONGO_INITDB_DATABASE="meltcheck" -d mongo
docker pull redis
docker run --name redis -p 6379:6379 --network=db-net -d redis
docker run --name tgdeploy --network=db-net -d meltcheck

docker run -exec -it db mongo
db.auth('admin','ckdgusmongodb')
use meltcheck
db.createUser({
user:'telegram',
pwd:'ckdgusapicall',
roles:['dbOwner']
})