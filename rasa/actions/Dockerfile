FROM python:3.8.10
# FROM rasa

# RUN apt-get update -y && \
#     apt-get install -y python-pip python-dev

# We copy just the requirements.txt first to leverage Docker cache

WORKDIR /app

RUN pip install rasa

COPY . /app

RUN pip install -r requirements.txt

CMD [ "sh","-c","rasa run actions" ]