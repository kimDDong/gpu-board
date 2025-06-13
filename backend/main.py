from flask import Flask, jsonify
from flask_cors import CORS
import dashboard_api
import resources_api
import users_api

app = Flask(__name__)
app.register_blueprint(dashboard_api.app)
app.register_blueprint(resources_api.app)
app.register_blueprint(users_api.app)

CORS(app)

if __name__ == '__main__':
    app.run('0.0.0.0', port=8000, debug=True)