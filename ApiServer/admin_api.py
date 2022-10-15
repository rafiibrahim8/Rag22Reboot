from traceback import format_exc
from threading import Thread
import requests
from dbms import DBMS

class AdminAPI:
    def __init__(self, dbms: DBMS, env, notification_sender):
        self.__dbms = dbms
        self.__env = env
        self.__notification_sender = notification_sender
        self.__func_map = {
            'update_qr': self.__update_qr,
            'add_qr': self.__add_qr,
            'update_user': self.__update_user,
            'add_user': self.__add_user,
            'sync_sms_api': self.__sync_sms_api,
            'delete_user': self.__delete_user,
            'refresh_user_token': self.__refresh_user_token
        }

    def __add_user(self, data):
        if self.__dbms.get_user(data['username']):
            raise Exception('User already exists')
        self.__update_user(data)

    def __refresh_user_token(self, data):
        self.__dbms.refresh_user_token(data['username'])

    def __delete_user(self, data):
        self.__dbms.delete_user(data['username'])

    def __sync_sms_api(self, data):
        Thread(target=self.__sync_sms_api_impl).start()

    def __sync_sms_api_impl(self):
        try:
            headers = {'User-Agent': 'curl/7.68.0'}
            res = requests.get('https://sms.solutionsclan.com/api/sms/balance', params={'apiKey': self.__env['sms_api_key']}, headers=headers).json()
            balance = float(res['balance'])
            if balance < 75.0:
                self.__notification_sender.send_admin_notif(f'SMS sender balence is low. Currently have BDT {balance}.')

            for i in self.__dbms.get_all_undelivered_sms():
                sms_id, sms_dlvref = i['sms_id'], i['sms_dlvref']
                res = requests.get('https://sms.solutionsclan.com/api/sms/dlr', params={'dlrRef': sms_dlvref}, headers=headers).json()
                self.__dbms.mark_as_delevered(sms_id, int(res['report']['status']))
        except:
            self.__notification_sender.send_admin_notif(f'Exception Syncing SMS:\n{format_exc()}')

    def __update_qr(self, data):
        self.__dbms.update_qr_admin(**data)

    def __add_qr(self, data):
        qr_plain = data.pop('qr_code')
        self.__dbms.add_qr_admin(qr_plain, **data)


    def __update_user(self, data):
        self.__dbms.update_user(**data)

    def handle_req(self, req):
        try:
            func = self.__func_map.get(req['type'])
            func(req['data'])
            return True
        except:
            print(format_exc())
            self.__notification_sender.send_admin_notif(f'Exception in API:\n{format_exc()}')
            return False
