#!/bin/bash
python -m venv venv
source venv/bin/activate
export PIP_DEFAULT_TIMEOUT=100
pip install --upgrade pip
pip install -r requirements.txt
sleep 3
python main.py
