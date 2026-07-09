import urllib.request
try:
    response = urllib.request.urlopen('https://owenofsl.ovenx.shop/login')
    print("Status:", response.status)
    print(response.read().decode('utf-8'))
except Exception as e:
    print("Error:", e)
