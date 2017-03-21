#!/bin/sh

set -e

DIR=$(pwd)
python $DIR/kakao-py.py <email> <device uuid> < $DIR/password
