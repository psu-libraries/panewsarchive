# panewsarchive
A repository for the local fork of the Open ONI project for PSU Deployment.


# to run in docker compose

cd panewsarchive/

git submodule update --init --recursive (if pulling first time)

git submodule update --recursive (if already pulled)

docker-compose up --build

change ports in docker-compose.yml and dc-local.sh
