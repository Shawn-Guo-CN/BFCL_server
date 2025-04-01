import argparse
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import uvicorn
from asgiref.wsgi import WsgiToAsgi
from flask import Flask, jsonify, request

from bfcl.runners import PlainJsonRunner

app = Flask(__name__)

logger = logging.getLogger(__name__)
runner = PlainJsonRunner()


@app.route("/call", methods=["GET"])
def call():
    logging.info(f"Received the following request to execute: {request.json}")
    func_call = request.json
    response = runner.run(func_call["id"], func_call["completion"])
    logging.info(f"Returning the following result: {response}")
    return jsonify(response)


@app.route("/calls", methods=["GET"])
def calls():
    # NOTE: input is a list of tool-calls
    logging.info(f"Received the following requests to execute: {request.json}")
    func_calls = request.json

    # Get the number of workers from the app config
    max_workers = app.config.get("NUM_WORKERS", 16)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(runner.run, func_call["id"], func_call["completion"]) for func_call in func_calls]
        responses = [future.result() for future in futures]
    return jsonify(responses)


def setup_logging(log_dir: str = "./logs"):
    os.makedirs(log_dir, exist_ok=True)
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join(log_dir, f"bfcl_server_{current_time}.log")
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def init_logging(host, port, num_workers=16):
    setup_logging()
    logger.info(f"Server starting on http://{host}:{port} with {num_workers} workers")
    logger.info(f"Starting the simulator server at {datetime.now()}")


def main():
    parser = argparse.ArgumentParser(description="BFCL Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to listen on")
    parser.add_argument("--port", type=int, default=1123, help="Port to listen on")
    parser.add_argument("--num_workers", type=int, default=16, help="Number of workers for concurrent requests")
    args = parser.parse_args()
    init_logging(args.host, args.port, args.num_workers)
    app.config["NUM_WORKERS"] = args.num_workers
    uvicorn.run(WsgiToAsgi(app), host=args.host, port=args.port)


if __name__ == "__main__":
    main()
