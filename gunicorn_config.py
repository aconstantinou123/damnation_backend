bind = '0.0.0.0:5000'
errorlog = '-'
loglevel = 'debug'
accesslog = '-'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
# Environment variables
raw_env = [
    "APP_PORT=5000",
    "FLASK_APP=app.py",
    "FLASK_ENV=development",
    "FLASK_DEBUG=1",
    "SENDFILE=1",
    "SECRET_KEY=\xe1_\xd8d7B\x95\xcf\xf6}A\xf4T-\xb0\xbap!_\xd9\xb8\x18\xfe~"
]