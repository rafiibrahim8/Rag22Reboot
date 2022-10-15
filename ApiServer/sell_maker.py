import re
from dbms import DBMS

class SellMaker:
    def __init__(self, dbms:DBMS, notification_sender):
        self.__dbms = dbms
        self.__notification_sender = notification_sender

    def __validate_sell(self, req):
        kwargs = dict()
        kwargs['qr_code'] = req.get('qr_text')
        if len(req.get('customer_name').strip()) < 1:
            return False, None
        kwargs['buyer_name'] = req.get('customer_name').strip()
        try:
            if int(req.get('customer_amount').strip()) < 1:
                return False, None
            if not re.fullmatch("(?:\\+88|88)?(?:01[3-9]\\d{8})", req.get('customer_phone').strip()):
                return False, None
        except:
            return False, None
        kwargs['amount'] = int(req.get('customer_amount').strip())
        kwargs['buyer_phone'] = req.get('customer_phone').strip()[-11:]
        kwargs['seller'] = self.__dbms.get_user(token=req.get('seller_token')).username

        return True, kwargs

    def make_sell(self, req):
        qr = self.__dbms.get_qr_by_code(req['qr_text'])
        user = self.__dbms.get_user(token=req['seller_token'])
        if not self.__dbms.is_valid_qr(req['qr_text']):
            self.__dbms.add_counterfeit_qr_sell(req['qr_text'], user.username)
            return False
        
        if qr.is_sold and user.permission_level < 3:
            return False
        
        if user.permission_level < 2:
            return False

        status, kwargs = self.__validate_sell(req)
        if not status:
            return False
        print(kwargs)
        is_new = self.__dbms.update_qr_sell(**kwargs)

        self.__notification_sender.ping_sell_webhook()        
        self.__notification_sender.send_dicord_notif(kwargs['qr_code'].split(':')[2], kwargs['seller'], is_new, kwargs['buyer_phone'], kwargs['buyer_name'], kwargs['amount'])
        self.__notification_sender.send_sell_sms(kwargs['buyer_phone'], kwargs['buyer_name'], kwargs['amount'], is_new, kwargs['qr_code'].split(':')[2])

        return True
