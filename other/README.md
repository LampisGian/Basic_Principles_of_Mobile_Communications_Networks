# setup env

**Αρχικοποίηση Env**

deactivate

rm -rf /Users/vasiliskyriakos/Desktop/2025/5G\ Technologies/venv

pip install --upgrade pip

python3 -m venv venv

source venv/bin/activate

docker --version  # Εκδόση Docker

python3 --version  # Εκδόση python

pip install -r requirements.txt

**Install Docker**

pip install docker  # install docker

pip show docker  # see if it is installed

**Networks**

docker ps

docker network ls

docker network inspect base_station_1

docker network inspect base_station_2


**Install Mac**

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt

python script.py

python monitor_global.py

cd logs 

tail -f monitor_logs.txt

tail -f cooldown_logs.txt

tail -f connection_logs.txt


# remove env

deactivate

rm -rf /Users/vasiliskyriakos/Desktop/2025/5G\ Technologies/venv

# logs run
tail -f filename.txt
