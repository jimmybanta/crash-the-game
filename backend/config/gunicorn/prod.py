"""Gunicorn *productionn* config file"""

# Django WSGI application path in pattern MODULE_NAME:VARIABLE_NAME
wsgi_app = "backend.asgi:application"
# The granularity of Error log outputs
loglevel = "debug"
# The number of worker processes for handling requests
workers = 3
# Worker class
worker_class = "uvicorn.workers.UvicornWorker"
# Timeout period
timeout = 120
# The socket to bind
bind = "0.0.0.0:8000"
# Restart workers when code changes (development only!)
reload = False
# Write access and error info to /var/log
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
# Redirect stdout/stderr to log file
capture_output = True
# PID file so you can easily fetch process ID
pidfile = "/var/run/gunicorn/process.pid"
# Daemonize the Gunicorn process (detach & enter background)
daemon = True
