docker compose --env-file .env1.0 -p apiv1  up -d
docker compose --env-file .env2.0 -p apiv2  up -d
docker compose --env-file .env3.0 -p apiv3  up -d


docker compose -p apiv1  logs api
docker compose -p apiv1  logs db
docker compose -p apiv1  start api

docker compose -p apiv2  logs api
docker compose -p apiv2  logs db
docker compose -p apiv2  start api

docker compose -p apiv3  logs api
docker compose -p apiv3  logs db
docker compose -p apiv3  start api