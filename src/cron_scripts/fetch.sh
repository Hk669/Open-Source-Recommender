#!/bin/sh

cd /home/ubuntu/Open-Source-Recommender/

source /home/ubuntu/Open-Source-Recommender/venv/bin/activate

python3 /src/cron_scripts/fetch_data.py

deactivate

