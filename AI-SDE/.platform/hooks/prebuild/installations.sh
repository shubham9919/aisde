#!/bin/bash
sudo su
y Yes | sudo yum install npm
echo "starting up the prebuild script"
source activate
y yes | sudo yum install curl gcc-c++ make
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source ~/.bashrc
source "$HOME/.cargo/env"
echo $PATH
rustc --version
source ~/.bashrc
y Yes | pip install psycopg2-binary
source ~/.bashrc
