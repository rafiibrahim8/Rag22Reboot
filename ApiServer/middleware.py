from dbms import DBMS
from password_factory import PasswordFactory, HashedQRFactory
from sell_maker import SellMaker
from admin_api import AdminAPI
from notification_sender import NotificationSender
from edit_sell import EditSell

class Middleware:
    def __init__(self, env):
        self.__password_factory = PasswordFactory(env.get('pepper'))
        self.__hashed_qr_factory = HashedQRFactory(env.get('pepper'))
        self.__dbms = DBMS(password_factory = self.__password_factory, hashed_qr_factory=self.__hashed_qr_factory)
        self.__notification_sender = NotificationSender(self.__dbms, env)
        self.__sell_maker = SellMaker(self.__dbms, self.__notification_sender)
        self.__admin_api = AdminAPI(self.__dbms, env, self.__notification_sender)
        self.__edit_sell = EditSell(self.__dbms, self.__notification_sender)
        self.__helpline = env.get('helpline') or 'admin'
    
    def __login_using_token(self, token):
        user = self.__dbms.get_user(token=token)
        if not user:
            return {'status':'expired'}, 400
        if not user.active:
            return {'status':'Inactive'}, 400
        return {'seller_token': token, 'seller_name': user.full_name}, 200

    def __login_using_password(self, username, password):
        user = self.__dbms.get_user(username=username)
        if not user:
            return {'status': 403}, 403
        if not user.active:
            return {'status': 403}, 403
        if not self.__password_factory.is_valid_login(user.password, password):
            return {'status': 403}, 403
        return {'seller_token': user.token, 'seller_name': user.full_name}, 200

    def login(self, req):
        if(req.get('seller_token')):
            return self.__login_using_token(req.get('seller_token'))
        if(req.get('password') and req.get('username')):
            return self.__login_using_password(req.get('username'), req.get('password'))
        return {'status': 400}, 400
    
    def is_authenticated(self, req):
        if not req.get('seller_token'):
            return False
        _, status = self.__login_using_token(req.get('seller_token'))
        return status==200

    def handle_qr(self, req):
        if not self.is_authenticated(req):
            return {'status': 400}, 400
        qr = self.__dbms.get_qr_by_code(req['qr_text'])
        user = self.__dbms.get_user(token=req['seller_token'])
        if not self.__dbms.is_valid_qr(req['qr_text']):
            self.__dbms.add_counterfeit_qr_sell(req['qr_text'], user.username)
            return {'status': 400}, 400
        if user.permission_level < 2 and not qr.is_sold:
            return {'status': 401}, 401
        
        editable = not qr.is_sold or user.permission_level > 2

        res = {
            'customer_name': qr.buyer_name or '',
            'customer_phone': qr.buyer_phone or '',
            'customer_amount': qr.amount or '',
            'qrid': req['qr_text'].split(':')[2],
            'customer_is_edit': qr.is_sold,
            'editable': editable,
            'extra_text': '' if editable else f'Contact {self.__helpline} for help',
            'qr_text': req['qr_text']
        }
        return res, 200

    def __has_all_params_sell(self, req):
        required = ['customer_name', 'customer_phone', 'customer_amount', 'qr_text']
        for i in required:
            if not req.get(i):
                return False
        return True
    
    def __has_all_params_edit(self, req):
        required = ['customer_name', 'customer_phone', 'customer_amount', 'qrid']
        for i in required:
            if not req.get(i):
                return False
        return True

    def handle_sell(self, req):
        if not self.is_authenticated(req) or not self.__has_all_params_sell(req):
            return {'status': 400}, 400
        if self.__sell_maker.make_sell(req):
            return {'status': 200}, 200
        return {'status': 400}, 400

    def edit_sell(self, req):
        if not self.is_authenticated(req):
            return {'status': 400}, 400
        user = self.__dbms.get_user(token=req['seller_token'])
        if not (user.permission_level > 2):
            return {'status': 403}, 403
        if req.get('type') == 'get_info':
            return self.__edit_sell.get_info(req.get('qrid', '').strip())
        if req.get('type') == 'set_info' and self.__has_all_params_edit(req):
            return self.__edit_sell.set_info(req['customer_name'], req['customer_phone'], req['customer_amount'], req['qrid'], user.username)
        return {'status': 400}, 400

    def handle_admin_api(self, req):
        if self.__admin_api.handle_req(req):
            return 'OK!', 200
        return 'Bad Request!', 400


class RequestValidator:
    @staticmethod
    def validate(req, validate_qr=False):
        if not req:
            return False
        for k, v in req.items():
            if not isinstance(v, str):
                return False
        if validate_qr:
            return req.get('qr_text') and len(req['qr_text'].split(':')) == 3
        else:
            return True
