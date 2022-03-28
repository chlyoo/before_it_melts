#
mongodb

docker pull mongo
docker network rm db-net
docker network create db-net
docker run --name db -p 27017:27017 --network=db-net -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=ckdgusmongodb -e MONGO_INITDB_DATABASE=meltcheck -d mongo
use meltcheck
db.createUser({
... user:'telegram',
... pwd:'ckdgusapicall',
... roles:['dbOwner']
... }
... )
docker exec -it db mongo

redis 

docker pull redis 
docker run --name redis -p 6379:6379 --network=db-net -d redis
docker exec -it redis sh -c "/bin/bash"

# workload
docker run -d --name tgdeploy --network=db-net meltdown
