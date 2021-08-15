FROM python:3

# Set the working directory to /app
WORKDIR /code

# Copy the current directory contents into the container at /app
COPY . /code

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 5000

# CMD [ "gunicorn", "--reload", "-w", "4", "--bind", "0.0.0.0:5000", "wsgi"]
CMD ["gunicorn", "--reload", "-c", "gunicorn_config.py", "-w", "4", "app:application"]