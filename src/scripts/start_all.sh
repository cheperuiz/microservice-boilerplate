#!/bin/bash

sh -x common/start_workers.sh &
python common/start_consumers.py
sh -x common/start_jupyter.sh