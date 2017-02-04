import requests

try:
    print(requests.get("http://172.17.0.2:80", timeout=3).content)
except:
    print("Couldn't connect to 172.17.0.2:80")
print(requests.get("http://192.168.99.100:80").content)
