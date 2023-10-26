sys-packages:
	# sudo apt install -y docker-compose
	sudo apt install python3-pip -y
	sudo pip3 install pipenv

pipenv:
	pipenv install -r requirements-dev.txt	

prepare: clean sys-packages pipenv build

build:
	docker-compose build

run:
	docker-compose up -d

run&draw:
	xhost +local:docker
	docker-compose up -d

restart:
	docker-compose restart

run-atm:
	pipenv run python atm/atm.py

run-fps:
	pipenv run python fps/fps.py

run-drone:
	pipenv run python drone/drone.py

test:
	pipenv run pytest -sv


clean:
	pipenv --rm
	rm -rf Pipfile*