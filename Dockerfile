FROM python:3.8.10

# RUN apt-get update -y && \
#     apt-get install -y python-pip python-dev

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt
# RUN pip install rasa

COPY . /app

ENTRYPOINT [ "python" ]
CMD [ "app.py" ]

# CMD [ "sh","-c","python app.pyw && cd rasa && rasa run --enable-api" ]
