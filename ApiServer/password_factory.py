import base64
import os
import hashlib

import utils

class PasswordFactory:
    def __init__(self, pepper=None, separator='$'):
        if not pepper:
            pepper = 'spicy'
        self.__pepper = pepper
        self.__separator = separator
    
    def mk_hashed_pwd(self, plain):
        salt = base64.b64encode(os.urandom(32)).decode('utf-8')
        return self.mk_hashed_pwd_with_salt(plain, salt)
    
    def mk_hashed_pwd_with_salt(self, plain, salt):
        hash = hashlib.sha512(f'{salt}{plain}{self.__pepper}'.encode('utf-8')).hexdigest()
        return f'{salt}{self.__separator}{hash}'
    
    def is_valid_login(self, from_db, from_user):
        salt, _ = from_db.split(self.__separator)
        from_local = self.mk_hashed_pwd_with_salt(from_user, salt)
        return utils.secure_compare(from_db, from_local)

class HashedQRFactory:
    def __init__(self, pepper=None, separator='$'):
        if not pepper:
            pepper = 'spicy'
        self.__pepper = pepper
        self.__separator = separator
    
    def mk_hashed_qr(self, plain):
        salt = base64.b64encode(os.urandom(32)).decode('utf-8')
        return self.mk_hashed_qr_with_salt(plain, salt)
    
    def mk_hashed_qr_with_salt(self, plain, salt):
        hash = hashlib.sha512(f'{salt}{plain}{self.__pepper}'.encode('utf-8')).hexdigest()
        return f'{salt}{self.__separator}{hash}'
    
    def is_valid_qr(self, from_db, from_user):
        salt, _ = from_db.split(self.__separator)
        from_local = self.mk_hashed_qr_with_salt(from_user, salt)
        return utils.secure_compare(from_db, from_local)
