import requests

url = 'http://localhost:8000'
myobj = {
    'id': 'id123',
    'rssi': -22,
    'company': "HP"
    }

x = requests.post(url, json=myobj)

print(x.text)