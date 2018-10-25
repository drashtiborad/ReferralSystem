#!/bin/bash

current_dir="`dirname \"$0\"`"
current_dir="`( cd \"$current_dir\" && pwd )`"

# MySQL Installation
export DEBIAN_FRONTEND="noninteractive"
sudo debconf-set-selections <<< "mysql-server mysql-server/root_password password rootpasswd"
sudo debconf-set-selections <<< "mysql-server mysql-server/root_password_again password rootpasswd"

sudo apt-key adv --keyserver pgp.mit.edu --recv-keys 5072E1F5
sudo apt update
sudo apt install -y mysql-server-5.7

mysql -u root --password=rootpasswd -e "CREATE USER 'drashti'@'localhost' IDENTIFIED BY 'abc123'"
mysql -u root --password=rootpasswd -e "GRANT ALL PRIVILEGES ON * . * TO 'drashti'@'localhost'"
mysql -u root --password=rootpasswd -e "FLUSH PRIVILEGES"
mysql -u root --password=rootpasswd -e "CREATE DATABASE referral_api"

sudo apt install -y python3
sudo apt install -y python3-pip
sudo apt install -y libmysqlclient-dev
sudo apt install -y gunicorn

sudo -H pip3 install -r ${current_dir}/requirements.txt

python3 ${current_dir}/manage.py makemigrations api
python3 ${current_dir}/manage.py migrate
cd ${current_dir}

gunicorn --bind localhost:8000 --workers 3 referral_api.wsgi --daemon

# Create test users
curl -XPOST localhost:8000/api/register?email=user1@test.com
curl -XPOST localhost:8000/api/register?email=user2@test.com
curl -XPOST localhost:8000/api/register?email=user3@test.com
curl -XPOST localhost:8000/api/register?email=user4@test.com
curl -XPOST localhost:8000/api/register?email=user5@test.com
curl -XPOST localhost:8000/api/register?email=user6@test.com
curl -XPOST localhost:8000/api/register?email=user7@test.com
curl -XPOST localhost:8000/api/register?email=user8@test.com
curl -XPOST localhost:8000/api/register?email=user9@test.com
curl -XPOST localhost:8000/api/register?email=user10@test.com
