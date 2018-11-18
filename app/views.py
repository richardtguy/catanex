from flask import render_template, abort
from app import app
import config

@app.route('/<account>')
def index(account):
	return render_template(
		'dashboard.html',
		account=account,
		mqtt_user=config.MQTT_USER,
		mqtt_password=config.MQTT_PASSWORD
	)