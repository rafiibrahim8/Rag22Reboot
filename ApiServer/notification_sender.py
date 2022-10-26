import json
import requests
from traceback import format_exc, print_exc
from threading import Thread
from dbms import DBMS

class NotificationSender:
    def __init__(self, dbms:DBMS, env):
        self.__sms_api_key = env['sms_api_key']
        self.__sms_api_id = env['sms_api_id']
        self.__sell_webhook = env['sell_webhook']
        self.__sell_webhook_token = env['sell_webhook_token']
        self.__suspicious_contact = env['suspicious_contact'] or '+8801537559644'
        self.__sms_api_header = {'User-Agent': 'curl/7.68.0'}
        self.__discord_hook = env.get('discord_notif_hook')
        self.__admin_hook = env.get('discord_admin_hook')
        self.__dbms = dbms

    def send_sell_sms(self, phone, name, amount, is_new=True, qrid=None):
        if is_new:
            self.__send_sell_sms_new(phone, name, amount)
        else:
            self.__send_sell_sms_update(phone, name, amount, qrid)
    
    def __send_sell_sms_update(self, phone, name, amount, qrid):
        qr = self.__dbms.get_qr_by_code(qrid)
        edit = json.loads(qr.edits)[-1]
        prev_amount = edit['amount']
        prev_name = edit['buyer_name']
        money_prev = ' ' if prev_amount==amount else f' of BDT {prev_amount}.00 '
        if prev_amount!=amount or name!=prev_name:
            modification_text = f'This is a modification of your previous entry{money_prev}with serial {qrid}.\n'
        else:
            modification_text = ''
        text = f'Dear {name},\nThank you for purchasing your t-shirt for BDT {amount}.00. Please bring your t-shirt and receipt on the concert day.\n{modification_text}'
        if prev_amount!=amount:
            text += f'If you find this SMS suspicious kindly contact {self.__suspicious_contact}.\n'
        text += "- Srinjoy '18"
        self.__send_sms_impl(phone, text)
    
    def __send_sms_impl(self, phone, text):
        jdata = {
            'apiKey': self.__sms_api_key,
            'contactNumbers': phone,
            'senderId': self.__sms_api_id,
            'textBody': text
        }
        Thread(target=self.__send_sms_impl_thread_func, args=(jdata,)).start()

    def __send_sms_impl_thread_func(self, data):
        try:
            res = requests.post('https://sms.solutionsclan.com/api/sms/send', json=data, headers=self.__sms_api_header).json()
            self.__dbms.update_sms(data['textBody'], res['dlrRef'], data['contactNumbers'])
        except:
            self.send_admin_notif(f'SMS Sending failed.\n{format_exc()}\n{json.dumps(data)}', False)

    def __send_sell_sms_new(self, phone, name, amount):
        text = f"Dear {name},\nThank you for purchasing your t-shirt for BDT {amount}.00. Please bring your t-shirt and receipt on the concert day.\n- Srinjoy '18"
        self.__send_sms_impl(phone, text)

    def __send_discord(self, url, text):
        try:
            requests.post(url, json={'content': text})
        except:
            print_exc()

    def send_dicord_notif(self, qr_sl, username, is_new, phone, name, amount):
        Thread(target=self.__send_dicord_notif_impl, args=(qr_sl, username, is_new, phone, name, amount)).start()

    def __send_dicord_notif_impl(self, qr_sl, username, is_new, phone, name, amount):
        if not self.__discord_hook:
            return
        x = 'sold a t-shirt' if is_new else 'updated a sell'
        text = f'{username} just {x}.\nSL: {qr_sl}\nPhone: {phone}\nName: {name}\nAmount: {amount}'
        Thread(target=self.__send_discord, args=(self.__discord_hook, text)).start()

    def send_admin_notif(self, text, new_thread=True):
        if new_thread:
            Thread(target=self.__send_discord, args=(self.__admin_hook, text)).start()
        else:
            self.__send_discord(self.__admin_hook, text)

    def ping_sell_webhook(self):
        Thread(target=self.__ping_sell_webhook).start()

    def __ping_sell_webhook(self):
        try:
            requests.get(self.__sell_webhook, params={'token': self.__sell_webhook_token})
        except:
            print_exc()
