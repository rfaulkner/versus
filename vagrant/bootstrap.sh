#!/usr/bin/env bash

#   Core Packages
#   -------------

apt-get update
apt-get install -y apache2
apt-get install -y libapache2-mod-wsgi

rm -rf /var/www
ln -fs /vagrant /var/www
apt-get install -y gfortran libopenblas-dev liblapack-dev
apt-get install -y g++


#   General Packages
#   ---------------

apt-get install -y git
apt-get install -y vim
apt-get install -y redis-server
apt-get install -y curl


#   MySQL
#   -----

apt-get install -y mysql-server
apt-get install -y mysql-client

# For now do this part manually

# mysqladmin -u root -h localhost password '{%mysql_password%}'
# mysqladmin -u root -h {%hostname%} password '{%mysql_password%}'


#   Python Packages
#   ---------------

apt-get install -y python-dev
apt-get install -y python-pip
apt-get install -y python-numpy python-scipy


#   Hadoop Packages
#   ---------------

apt-get -y install software-properties-common
apt-get -y install python-software-properties

add-apt-repository ppa:webupd8team/java
apt-get -y update && sudo apt-get upgrade
apt-get -y install oracle-java7-installer

# Setup hadoop user
sudo addgroup hadoop
sudo adduser --ingroup hadoop hduser

add-apt-repository ppa:hadoop-ubuntu/stable
apt-get -y update && sudo apt-get upgrade
apt-get -y install hadoop
