FROM python:3.11-slim

WORKDIR /app
COPY load_generator.py .

RUN pip install kafka-python prometheus_client

ENTRYPOINT ["python", "load_generator.py"]
