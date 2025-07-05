from flask import Blueprint

charging_bp = Blueprint('charging', __name__, url_prefix='/charging')

from . import routes
