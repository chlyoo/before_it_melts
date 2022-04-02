# Telegram Bot for before_it_melts

## INFRA

### DB : redis, mongodb

#### REDIS

Usage : Key-Value storage for subscriptor list

#### MONGODB

Usage : NoSQL database for storaging crawled menu data

---

### How to setup infra (docker)

#### docker-network 

docker network create db-net

#### mongodb
``` shell
docker pull mongo
docker volume create --name=mongodata
docker run --restart unless-stopped --name db -p 27017:27017 --network=db-net -v mongodata:/data/db -e MONGO_INITDB_ROOT_USERNAME=<DB_ADMIN_NAME> -e MONGO_INITDB_ROOT_PASSWORD=<DB_ADMIN_PW> -e MONGO_INITDB_DATABASE=<INIT_DATABASE> --entry-point=mongosh -d mongo
```
##### Basic Authentication setup

`docker exec -it db mongo -u <MONGO_INITDB_ROOT_USERNAME> -p <MONGO_INITDB_ROOT_PASSWORD>`
`use meltcheck`

```
db.createUser({
user:'<ID_FOR_MONGODB_USER>',
pwd:'<PASSWORD_FOR_MONGODB_USER>',
roles:['dbOwner']
})
```
## redis 

```
docker pull redis 
docker volume create --name=redisdata
docker run --restart unless-stopped --name redis -p 6379:6379 -v c:\data\redis:/usr/local/etc/redis -v redisdata:/data --network=db-net -d redis redis-server /usr/local/etc/redis/redis.conf --appendonly yes
```

# workload

docker run --restart unless-stopped --name tgdeploy --network=db-net -d meltcheck
