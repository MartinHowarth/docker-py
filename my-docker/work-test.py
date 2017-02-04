import docker
from datetime import datetime
import time
client = docker.DockerClient(base_url="tcp://192.168.99.100:2375")


def rebuild_with_print(dockerfile):
    try:
        client.api.remove_image(dockerfile, force=True)
    except docker.errors.ImageNotFound:
        pass
    build = client.api.build(path="./", dockerfile=dockerfile + ".dockerfile", pull=True, rm=True, tag=dockerfile)
    for bi in build:
        print(bi)


def restart_work_server():
    return client.containers.run(
        "work-server",
        # ports={
        #     '80/tcp': '80',
        # },
        # network_mode='bridge',
        detach=True
    )


def start_worker(host_port):
    return client.containers.run(
        "work-client",
        ports={
            '80/tcp': str(host_port),
        },
        network_mode='bridge',
        detach=True
    )


def kill_all():
    for cont in client.containers.list():
        cont.kill()
        cont.remove()



# rebuild_with_print("work-server")
# rebuild_with_print("work-client")

kill_all()
serv = restart_work_server()
time.sleep(1)

# worker = start_worker(81)
# print(worker.id)
# log_stream = worker.logs(stream=True)
# for log in log_stream:
#     print(log)


workers = [start_worker(81 + i) for i in range(10)]
