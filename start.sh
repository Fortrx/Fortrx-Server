#!/bin/sh

echo "Waiting for DB..."
sleep 3

echo "Running migrations..."
alembic upgrade head

echo "Starting app..."
exec python run.py