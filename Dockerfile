FROM python:3

# Set the working directory to /app
WORKDIR /code

RUN mkdir /code/app

# Copy the current directory contents into the container at /app
COPY ./app/ /code/app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r app/requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 5000

COPY gunicorn_config.py /code

CMD [ "gunicorn", "--reload", "-c", "gunicorn_config.py", "-w", "4", "app:create_app()"]
