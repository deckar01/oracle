import waitress

from . import app


waitress.serve(app, listen='0.0.0.0:8081')
