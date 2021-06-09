FROM python:3.7-alpine

RUN pip install protobuf && \
    pip install --upgrade google && \
    pip install is-msgs && \
    pip install is-wire && \
    pip install celery && \
    pip install --upgrade protobuf


COPY src /app

WORKDIR app/project/robot

ENTRYPOINT ["python", "robot.py"]
