#
mongodb

docker pull mongo
docker network rm db-net
docker network create db-net
docker run --name db -p 27017:27017 --network=db-net -d mongo
docker exec -it db mongo
