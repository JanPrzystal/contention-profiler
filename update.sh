#!/bin/bash
git restore .
git fetch
git pull

source venv/bin/activate
pip install --upgrade -r requirements.txt
