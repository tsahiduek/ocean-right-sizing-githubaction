FROM python:3.8

WORKDIR /app
ADD resource_mutator.py /app
ADD requirements.txt /app
RUN pip install -r /app/requirements.txt 
RUN chmod +x /app/resource_mutator.py


# Code file to execute when the docker container starts up (`entrypoint.sh`)
ENTRYPOINT [ "python", "./resource_mutator.py" ]