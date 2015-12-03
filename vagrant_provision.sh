#!/usr/bin/env bash

# Prerequisites
sudo apt-get update
sudo apt-get install -y python-pip python-dev vim

# Mysql
sudo debconf-set-selections <<< "mysql-server mysql-server/root_password password \"''\""
sudo debconf-set-selections <<< "mysql-server mysql-server/root_password_again password \"''\""
sudo apt-get install -y mysql-server libmysqlclient-dev

mysql -u root -e "CREATE DATABASE IF NOT EXISTS spaces;"
mysql -u root -e "GRANT ALL PRIVILEGES ON spaces.* TO 'spaceman'@'localhost'; FLUSH PRIVILEGES;"

# Python libs
sudo pip install django
sudo pip install mysql-python

# Run migrations
cd /vagrant/
python manage.py migrate

#
# Shell goodies
#
BASH_PROFILE=/home/vagrant/.profile

echo "Setting up $BASH_PROFILE..."
touch $BASH_PROFILE

# Get django bash completion script
DJANGO_COMPLETE=/home/vagrant/.django_bash_completion
if [ ! -f $DJANGO_COMPLETE ]; then
  echo "Downloading .django_bash_completion..."
  curl -s -o $DJANGO_COMPLETE https://raw.githubusercontent.com/django/django/master/extras/django_bash_completion 
  echo "source $DJANGO_COMPLETE" >> $BASH_PROFILE
fi

# 'runserver' Alias
if ! grep -q 'alias runserver' $BASH_PROFILE ; then
  echo "Adding alias 'runserver'..."
  echo "alias runserver=\"python /vagrant/manage.py runserver 0.0.0.0:8000\"" >> $BASH_PROFILE
fi

chown vagrant $BASH_PROFILE $DJANGO_COMPLETE
chmod 755 $DJANGO_COMPLETE

