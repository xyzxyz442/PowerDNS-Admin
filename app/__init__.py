from werkzeug.contrib.fixers import ProxyFix
from flask import Flask, request, session, redirect, url_for
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy as SA
from flask_migrate import Migrate
from flask_oauthlib.client import OAuth
from sqlalchemy.exc import OperationalError

# subclass SQLAlchemy to enable pool_pre_ping
class SQLAlchemy(SA):
    def apply_pool_defaults(self, app, options):
        SA.apply_pool_defaults(self, app, options)
        options["pool_pre_ping"] = True


from app.assets import assets

app = Flask(__name__)
app.config.from_object('config')
app.wsgi_app = ProxyFix(app.wsgi_app)

assets.init_app(app)

#### CONFIGURE LOGGER ####
from app.lib.log import logger
logging = logger('powerdns-admin', app.config['LOG_LEVEL'], app.config['LOG_FILE']).config()

login_manager = LoginManager()
login_manager.init_app(app)
db = SQLAlchemy(app)            # database
migrate = Migrate(app, db)      # flask-migrate
oauth_client = OAuth(app)       # oauth

if app.config.get('SAML_ENABLED') and app.config.get('SAML_ENCRYPT'):
    from app.lib import certutil
    if not certutil.check_certificate():
        certutil.create_self_signed_cert()

from app import models
from app import views
