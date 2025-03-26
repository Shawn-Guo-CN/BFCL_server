import argparse
import logging
import os
from datetime import datetime

import uvicorn
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
    response = runner.run(engine_input["id"], engine_input["completion"])
    logging.info(f"Returning the following result: {response}")
    return jsonify(response)


def setup_logging(log_dir: str = "./logs"):
    os.makedirs(log_dir, exist_ok=True)
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join(log_dir, f"bfcl_server_{current_time}.log")
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def init_logging(host, port):
    setup_logging()
    logger.info(f"Server starting on http://{host}:{port}")
    logger.info(f"Starting the simulator server at {datetime.now()}")


def main():
    parser = argparse.ArgumentParser(description="BFCL Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to listen on")
    parser.add_argument("--port", type=int, default=1123, help="Port to listen on")
    args = parser.parse_args()
    init_logging(args.host, args.port)
    uvicorn.run(WsgiToAsgi(app), host=args.host, port=args.port)


if __name__ == "__main__":
    main()
