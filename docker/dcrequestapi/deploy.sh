cd dcrequestapi;
docker build --no-cache -t docker.leibniz-lib.de:5000/dcrequestapi:latest .; docker push docker.leibniz-lib.de:5000/dcrequestapi:latest;
cd ..;
docker stack rm dcrequestapi;
docker stack deploy --with-registry-auth -c docker-compose-swarm.yml dcrequestapi;


