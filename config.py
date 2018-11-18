import os

# Cloud MQTT parameters for order completion notifications
MQTT_HOST = "m21.cloudmqtt.com"
MQTT_PORT = 17683
try:
	MQTT_USER = os.environ['MQTT_USER']
	MQTT_PASSWORD = os.environ['MQTT_PASSWORD']
except KeyError:
	MQTT_USER = None
	MQTT_PASSWORD = None

# Game parameters
OPENING_BALANCE = 100

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
	'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False