#

## docker network setup

docker network rm db-net
docker network create db-net

##mongodb

docker pull mongo
docker run --restart unless-stopped --name db -p 27017:27017 --network=db-net -v ~/data:/data/db -e MONGO_INITDB_ROOT_USERNAME=<DB_ADMIN_NAME> -e MONGO_INITDB_ROOT_PASSWORD=<DB_ADMIN_PW> -e MONGO_INITDB_DATABASE=<INIT_DATABASE> -d mongo
docker update  redis
### mongodb auth

docker exec -it db mongo -u <MONGO_INITDB_ROOT_USERNAME> -p <MONGO_INITDB_ROOT_PASSWORD>

db.auth(<MONGO_INITDB_ROOT_USERNAME>, <MONGO_INITDB_ROOT_PASSWORD>)
use meltcheck
db.createUser({
... user:'<ID_FOR_MONGODB_USER>',
... pwd:'<PASSWORD_FOR_MONGODB_USER>',
... roles:['dbOwner']
... }
... )

use subscriptors
db.createUser({
... user:'<ID_FOR_MONGODB_USER>',
... pwd:'<PASSWORD_FOR_MONGODB_USER>',
... roles:['dbOwner']
... }
... )

##redis 

docker pull redis 
docker run --restart unless-stopped --name redis -p 6379:6379 -v ~/data:/data --network=db-net -d redis
docker exec -it redis sh -c "/bin/bash"

# workload
docker run -d --name tgdeploy --network=db-net meltdown
