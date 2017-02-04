import requests
import time
import hashlib
from struct import unpack, pack

server_url = "http://172.17.0.2:80"
timeout = 3


class Worker:
    def __init__(self):
        self.worker_id = None
        self.payload = None
        self.target_maximum = None
        self.guess = None
        self.nonce = None
        self._last_work_time = 0
        self.new_worker_id()

    def new_worker_id(self):
        self.worker_id = int(requests.get(server_url + "/worker_id", timeout=timeout).content)

    def get_work(self):
        """
        Receive a task.
        Unblocks :func:`~Worker.request_work`
        :param payload: Payload of the work to be solved.
        :param target_maximum: Target maximum of the work to be solved (determines difficulty).
        """
        response = requests.get(server_url + "/generate_work/", params={
            'worker_id': self.worker_id
        }, timeout=timeout)
        values = response.json()
        namespace = {}
        exec("pay = %s" % values['payload'], namespace)
        payload = namespace['pay']
        self.payload = payload
        self.target_maximum = values['target_maximum']
        if not self.payload:
            # We won't be given another payload if we haven't solved the last one we got.
            raise ValueError("Already have unsolved work.")

    def do_work(self):
        """
        Actually work out the solution to the task set.
        """
        if self.payload is None or self.target_maximum is None:
            return

        start_time = time.time()
        guess = 99999999999999999999
        nonce = 0
        payload = self.payload
        while guess > self.target_maximum:
            nonce += 1
            guess, = unpack('>Q', hashlib.md5(hashlib.md5(pack('>Q', nonce) + payload).digest()).digest()[0:8])

        end_time = time.time()
        self.nonce = nonce
        self.guess = guess
        self._last_work_time = end_time - start_time

    def is_work_valid(self):
        response = requests.get(server_url + "/validate_work/", params={
            'worker_id': self.worker_id,
            'guess': self.guess,
            'nonce': self.nonce
        }, timeout=timeout)
        return response.json()['result']


a = Worker()
for i in range(10):
    a.get_work()
    a.do_work()
    print(a.is_work_valid())
    time.sleep(1)
