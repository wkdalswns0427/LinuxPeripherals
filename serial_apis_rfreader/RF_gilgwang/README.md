# RF_utility

uvicorn app:app --host 0.0.0.0 --reload --port 6677

sudo chmod 666 /dev/ttyS0

docker run --rm -p 6677:6677 --device=/dev/ttyS1 rf:latest