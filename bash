#!/bin/bash
apt-get update -y
apt-get install git -y
cd /home/ubuntu
git clone https://github.com/fortrx/fortrx-server
chown -R ubuntu:ubuntu /home/ubuntu/fortrx-server
cd fortrx-server
