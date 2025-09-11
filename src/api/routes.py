from flask import Flask, jsonify
from flask_cors import CORS

def create_api(consumer_service):
    app = Flask(__name__)
    CORS(app)

    @app.route("/api/heartbeat", methods=["GET"])
    def get_heartbeat():
        with consumer_service.lock:
            return jsonify(consumer_service.latest_heartbeat)

    @app.route("/api/heartbeat/analysis", methods=["GET"])
    def get_heartbeat_analysis():
        with consumer_service.lock:
            return jsonify({
                "latest": consumer_service.latest_heartbeat,
                "alerts": consumer_service.alerts[-2:]  # last 2 alerts
            })

    @app.route("/api/activity", methods=["GET"])
    def get_activity():
        with consumer_service.lock:
            return jsonify({"total_steps": consumer_service.total_steps})



    return app
