FROM python:3.8.12-alpine3.13

ENV GROUP_ID=1000 \
    USER_ID=1000

# Set the working directory to /app
WORKDIR /code

RUN mkdir /code/app

# Copy the current directory contents into the container at /app
COPY ./app/ /code/app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r app/requirements.txt

RUN addgroup -g $GROUP_ID code
RUN adduser -D -u $USER_ID -G code code -s /bin/sh

USER code

# Make port 80 available to the world outside this container
EXPOSE 5000

COPY gunicorn_config.py /code

CMD [ "gunicorn", "--reload", "-c", "gunicorn_config.py", "-w", "4", "app:create_app()"]
