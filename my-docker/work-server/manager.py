from flask import Flask, request, jsonify
import time
import hashlib
import logging
from struct import unpack, pack

app = Flask(__name__)


def verify_payload(payload: bytes, guess: int, nonce: int):
    return unpack('>Q', hashlib.md5(hashlib.md5(pack('>Q', nonce) + payload).digest()).digest()[0:8])[0] == guess


worker_count = 0
workers = {}

difficulty = 10000

target_maximum = 2 ** 64 / difficulty

message = "Congratulations, you found an Easter egg. Have a cookie."


def _generate_payload() -> bytes:
    """
    Generate a unique payload.
    :return: Hash of a unique string.
    """
    payload = (str(time.time()) + message).encode()
    return hashlib.md5(payload).digest()


@app.route("/worker_id/")
def generate_worker_id() -> int:
    """
    Generate and a unique worker id.
    Worker ID should never be 0.
    """
    global worker_count
    worker_count += 1
    return jsonify(worker_count)


@app.route("/generate_work/", methods=['GET'])
def generate_work() -> (bytes, int):
    """
    Get and return a work task.
    Each worker is only allowed one task at once.
    A task consists of a payload, and the target maximum value.
    :param worker_id: ID of the worker requesting work.
    """
    args = request.args.to_dict()
    worker_id = args['worker_id']

    # Only allow each worker to have one workload at a time
    if worker_id in workers.keys():
        payload = b''
    else:
        payload = _generate_payload()
        workers[worker_id] = payload
    return jsonify(
        payload=str(payload),
        target_maximum=target_maximum
    )


@app.route("/validate_work/", methods=['GET'])
def validate_work() -> bool:
    """
    Check that the given solution to a task correctly solves the task given to that worker.
    :param worker_id: ID of the worker who did the work
    :param guess: Guess part of the solution.
    :param nonce: Nonce part of the solution.
    """
    worker_id = request.args.get('worker_id')
    guess = int(request.args.get('guess'))
    nonce = int(request.args.get('nonce'))
    result = False
    if worker_id in workers.keys():
        payload = workers[worker_id]
        if verify_payload(payload, guess, nonce):
            # Clear them from the current worker-task mapping.
            del workers[worker_id]
            result = True
        else:
            result = False
    return jsonify(result=result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
