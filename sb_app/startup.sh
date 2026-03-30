#!/bin/bash
cd /home/ec2-user/app
source venv/bin/activate
uvicorn m ain:app --host 0.0.0.0 --port 8000