import requests
import json
import sys

URL = 'https://api.rag22reboot.ece17.rocks/admin_api'
# URL = 'http://127.0.0.1:65014/admin_api'

class Admin:
    def __init__(self, url):
        with open('env.json') as f:
            self.__token = json.load(f)['api_token']
        self.__url = url

    def add_user(self, username, password, full_name, permission_level, active=True):
        print(f'Adding User.\nusername: {username}\npassword: {password}\nfull name: {full_name}')
        headers = {
            'Authorization': f'Bearer {self.__token}'
        }
        data = {
            'username': username,
            'password': password,
            'full_name': full_name,
            'active': active,
            'permission_level': permission_level
        }

        res = requests.post(self.__url, headers=headers, json={'type':'add_user', 'data': data})
        assert res.status_code == 200, res.text
        print('Success')

    def delete_user(self, username):
        headers = {
            'Authorization': f'Bearer {self.__token}'
        }
        data = {
            'username': username
        }
        assert requests.post(self.__url, headers=headers, json={'type':'delete_user', 'data': data}).status_code == 200
        print('Success')

    def add_qr(self, qr_code):
        headers = {
            'Authorization': f'Bearer {self.__token}'
        }
        data = {
            'qr_code': qr_code
        }
        assert requests.post(self.__url, headers=headers, json={'type':'add_qr', 'data': data}).status_code == 200

    def reset_qr(self, qr_sl):
        headers = {
            'Authorization': f'Bearer {self.__token}'
        }
        data = {
            'qr_sl': qr_sl
        }
        assert requests.post(self.__url, headers=headers, json={'type':'update_qr', 'data': data}).status_code == 200
        print('Success')

    def sync_sms(self):
        headers = {
            'Authorization': f'Bearer {self.__token}'
        }
        assert requests.post(self.__url, headers=headers, json={'type':'sync_sms_api', 'data': {}}).status_code == 200

    def add_qrs(self):
        with open('qrs.json','r') as f:
            qrs = json.load(f)
        for q in qrs:
            self.add_qr(q)

    def add_user_from_json(self, path):
        with open(path, 'r') as f:
            users = json.load(f)
        for i in users:
            self.add_user(**i)

if __name__ == '__main__':
    admin = Admin(URL)
    if len(sys.argv) > 1:
        admin.add_user(sys.argv[1], sys.argv[2], sys.argv[3])
    #admin.add_user('ibra','abc123','Ibrahim')
    admin.add_user_from_json('users.json')
    #admin.sync_sms()
    #admin.add_user()
    #admin.add_qrs()

