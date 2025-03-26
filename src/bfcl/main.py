import logging
import os
from datetime import datetime

from asgiref.wsgi import WsgiToAsgi
from flask import Flask, jsonify, request

from bfcl.runners import PlainJsonRunner

app = Flask(__name__)

logger = logging.getLogger(__name__)
runner = PlainJsonRunner()


@app.route("/execute", methods=["GET"])
def execute():
    logging.info(f"Received the following request to execute: {request.json}")
    engine_input = request.json
    result = runner.run(engine_input["prompt"], engine_input["completion"])
    logging.info(f"Returning the following result: {result}")
    return jsonify(result)


def setup_logging(log_dir: str = "./logs"):
    os.makedirs(log_dir, exist_ok=True)
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join(log_dir, f"bfcl_server_{current_time}.log")
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def log_server_info(host, port):
    setup_logging()
    logger.info(f"Server starting on http://{host}:{port}")
    logger.info(f"Starting the simulator server at {datetime.now()}")


def create_asgi_app(host="127.0.0.1", port=1123):
    log_server_info(host, port)
    return WsgiToAsgi(app)
