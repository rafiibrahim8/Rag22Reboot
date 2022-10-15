import re

from dbms import DBMS
from notification_sender import NotificationSender

class EditSell:
    def __init__(self, dbms:DBMS, notification_sender:NotificationSender):
        self.__dbms = dbms
        self.__notification_sender = notification_sender

    def __validate_edit(self, customer_name, customer_phone, customer_amount):
        if len(customer_name) < 1:
            return False
        try:
            if int(customer_amount) < 1:
                return False
            if not re.fullmatch("(?:\\+88|88)?(?:01[3-9]\\d{8})", customer_phone):
                return False
        except:
            return False
        return True

    def get_info(self, qrid):
        qr = self.__dbms.get_qr_by_code(qrid)
        if not qr or not qr.is_sold:
            return {'status': 401}, 401
        res = {
            'customer_name': qr.buyer_name,
            'customer_phone': qr.buyer_phone,
            'customer_amount': qr.amount,
            'qrid': qrid,
        }
        return res, 200

    def set_info(self, customer_name, customer_phone, customer_amount, qrid, username):
        ## <don't judge me please :p>
        customer_phone = customer_phone.strip()
        customer_name = customer_name.strip()[-11:]
        customer_amount = customer_amount.strip()
        qrid = qrid.strip()
        ## </don't judge me please :p>
        
        qr = self.__dbms.get_qr_by_code(qrid)
        if not qr or not qr.is_sold:
            return {'status': 401}, 401
        if not self.__validate_edit(customer_name, customer_phone, customer_amount):
            return {'status': 400}, 400
        
        customer_amount = int(customer_amount)

        self.__dbms.update_qr_sell(qrid, customer_name, customer_phone, customer_amount, username)

        self.__notification_sender.send_dicord_notif(qr_sl=qrid, username=username, is_new=False, phone=customer_phone, name=customer_name, amount=customer_amount)
        self.__notification_sender.send_sell_sms(phone=customer_phone, name=customer_name, amount=customer_amount, is_new=False, qrid=qrid)
        
        return {'status': 200}, 200
