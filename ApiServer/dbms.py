from datetime import datetime
import hashlib
from sqlalchemy import BigInteger, Float, create_engine, func, Integer, String, Column, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from traceback import format_exc
from threading import Lock, Thread
import time
import json
import os

from password_factory import HashedQRFactory

import utils

Base = declarative_base()
lock = Lock()

class WebsiteStuffs(Base):
    __tablename__ = 'website_stuffs'

    key = Column(String, primary_key=True)
    value = Column(String) 

class Users(Base):
    __tablename__ = 'users'
    username = Column(String, primary_key=True)
    full_name = Column(String)
    password = Column(String, unique=True)
    token = Column(String, unique=True)
    active = Column(Boolean, default=True)
    permission_level = Column(Integer, default=2)
    last_sell = Column(String)
    total_sell = Column(Integer, default=0)
    total_amount = Column(Float, default=0)
    extra_data = Column(String)

class SellInfo(Base):
    __tablename__ = 'sell_info'
    qr_sl = Column(String, primary_key=True)
    qr_hash = Column(String, nullable=False)
    is_sold = Column(Boolean, default=False)
    is_valid = Column(Boolean, default=True)
    epoch = Column(BigInteger)
    datetime = Column(String)
    buyer_name = Column(String)
    buyer_phone = Column(String)
    amount = Column(Integer)
    seller = Column(String)
    editor = Column(String)
    edits = Column(String)
    total_edits = Column(Integer, default=0)

    is_inside = Column(Boolean, default=False)
    inside_attempts = Column(Integer, default=0)

    extra_data = Column(String)

class CounterfeitQRSells(Base):
    __tablename__ = 'counterfeit_qr_sell'
    qr_code = Column(String, primary_key=True)
    attempted_by = Column(String)
    total_attempts = Column(Integer, default=1)

class CounterfeitQREntrys(Base):
    __tablename__ = 'counterfeit_qr_entry'
    qr_code = Column(String, primary_key=True)
    attempted_by = Column(String)
    total_attempts = Column(Integer, default=1)

class SMSInfo(Base):
    __tablename__ = 'sms_info'
    sms_id = Column(String, primary_key=True)
    sms_datetime = Column(String)
    sms_text = Column(String)
    sms_dlvref = Column(String)
    sent_status = Column(Integer)
    
class DBMS():
    def __init__(self, password_factory, hashed_qr_factory:HashedQRFactory):
        db_path = utils.read_config()['postgres_url']
        engine = create_engine(db_path)
        Base.metadata.create_all(engine)
        self.dbSession = sessionmaker(engine)()
        self.__password_factory = password_factory
        self.__hashed_qr_factory = hashed_qr_factory

        self.__keep_alive_thread = Thread(target=self.__keep_alive)
        self.__keep_alive_thread.daemon = True
        self.__keep_alive_thread.start()
    
    def __keep_alive(self, interval=30):
        while True:
            try:
                res = self.dbSession.execute('SELECT 1').fetchall()
                print(res)
            except:
                print(format_exc())
            time.sleep(interval)
    
    def update_sms(self, sms_text, sms_dlvref, sent_status=1):
        sms_id = hashlib.sha256(os.urandom(1024)).hexdigest()
        sms_datetime = datetime.now(utils.BDT()).strftime('%Y-%m-%d %H:%M:%S')
        self.dbSession.add(SMSInfo(sms_text=sms_text, sms_dlvref=sms_dlvref, sent_status=sent_status, sms_id=sms_id, sms_datetime=sms_datetime))
        DBMS.commit_session(self.dbSession)

    def mark_as_delevered(self, sms_id, status=0):
        sms = self.dbSession.query(SMSInfo).filter_by(sms_id=sms_id).first()
        if sms:
            sms.sent_status = status
            DBMS.commit_session(self.dbSession)
        
    def get_all_undelivered_sms(self):
        sells = self.dbSession.query(SMSInfo).filter(SMSInfo.sent_status > 0).all()
        return utils.sql_all_to_json(sells)

    def get_user(self, username=None, token=None):
        user=None
        if username:
            user = self.dbSession.query(Users).filter_by(username=username).first()
        elif token:
            user = self.dbSession.query(Users).filter_by(token=token).first()
        return user

    def get_qr_by_code(self, qr_code):
        if len(qr_code.split(':')) == 3:
            qr_sl = qr_code.split(':')[2]
        else:
            qr_sl = qr_code
        return self.dbSession.query(SellInfo).filter_by(qr_sl=qr_sl).first()
    
    def is_valid_qr(self, qr_code):
        qr = self.get_qr_by_code(qr_code)
        if not qr:
            return False
        return self.__hashed_qr_factory.is_valid_qr(qr.qr_hash, qr_code)

    def update_qr_sell(self, qr_code, buyer_name, buyer_phone, amount, seller):
        is_new_sell = True
        qr = self.get_qr_by_code(qr_code)
        now_datetime = datetime.now(utils.BDT()).strftime('%Y-%m-%d %H:%M:%S')
        if qr.is_sold: # editing a sell
            user = self.dbSession.query(Users).filter_by(username=qr.seller).first()
            qr.edits = utils.add_or_append_edits(qr)
            qr.total_edits += 1
            is_new_sell = False
            qr.editor = seller
            user.total_amount -= qr.amount
        else: # new sell
            user = self.dbSession.query(Users).filter_by(username=seller).first()
            qr.seller = seller
            user.total_sell += 1
            user.last_sell = now_datetime

        qr.buyer_name = buyer_name
        qr.buyer_phone = buyer_phone
        qr.amount = amount
        qr.is_sold = True
        qr.epoch = int(time.time()*1000)
        qr.datetime = now_datetime

        user.total_amount += amount
        DBMS.commit_session(self.dbSession)
        return is_new_sell

    def add_counterfeit_qr_sell(self, qr, username):
        cqr = self.dbSession.query(CounterfeitQRSells).filter_by(qr_code=qr).first()
        if cqr is None:
            self.dbSession.add(CounterfeitQRSells(qr_code=qr, attempted_by=json.dumps([username])))
        else:
            cqr.total_attempts += 1
            current_attempts = json.loads(cqr.attempted_by)
            current_attempts.append(username)
            cqr.attempted_by = json.dumps(current_attempts)
        DBMS.commit_session(self.dbSession)

    def update_user(self, username, password, full_name, permission_level, active=True):
        user = self.dbSession.query(Users).filter_by(username=username).first()
        password = self.__password_factory.mk_hashed_pwd(password)
        token = hashlib.sha512(os.urandom(2048)).hexdigest()
        if user is None:
            self.dbSession.add(Users(username=username, password=password, permission_level=permission_level, full_name=full_name, active=active, token=token))
        else:
            user.password = password
            user.full_name = full_name
            user.active = active
            user.token = token
        DBMS.commit_session(self.dbSession)

    def refresh_user_token(self, username):
        user = self.dbSession.query(Users).filter_by(username=username).first()
        user.token = hashlib.sha512(os.urandom(2048)).hexdigest()
        DBMS.commit_session(self.dbSession)
    
    def delete_user(self, username):
        self.dbSession.query(Users).filter_by(username=username).delete()
        DBMS.commit_session(self.dbSession)

    def add_qr_admin(self, qr_plain, **kwargs):
        qr_hashed = self.__hashed_qr_factory.mk_hashed_qr(qr_plain)
        qr_sl = qr_plain.split(':')[2]
        kwargs['qr_hash'] = qr_hashed
        kwargs['qr_sl'] = qr_sl
        self.dbSession.query(SellInfo).filter_by(qr_sl=qr_sl).delete()
        self.dbSession.add(SellInfo(**kwargs))
        DBMS.commit_session(self.dbSession)

    def update_qr_admin(self, **kwargs):
        qr_hashed =  self.dbSession.query(SellInfo).filter_by(qr_sl=kwargs['qr_sl']).first().qr_hash
        self.dbSession.query(SellInfo).filter_by(qr_sl=kwargs['qr_sl']).delete()
        kwargs['qr_hash'] = qr_hashed
        self.dbSession.add(SellInfo(**kwargs))
        DBMS.commit_session(self.dbSession)

    def get_all_qrs(self):
        sells = self.dbSession.query(SellInfo).all()
        return utils.sql_all_to_json(sells, sort_by='epoch')

    def get_all_users(self):
        users = self.dbSession.query(Users).all()
        return utils.sql_all_to_json(users)

    def update_website_stuff(self, key, value, commit=True):
        stuff = self.dbSession.query(WebsiteStuffs).filter_by(key=key).first()
        if stuff == None:
            self.dbSession.add(WebsiteStuffs(key=key, value=json.dumps(value)))
        else:
            stuff.value = json.dumps(value)
        if commit:
            DBMS.commit_session(self.dbSession)

    def get_website_stuff(self, key):
        stuff = self.dbSession.query(WebsiteStuffs).filter_by(key=key).first()
        return stuff if stuff == None else json.loads(stuff.value)
    
    @staticmethod
    def commit_session(session):
        with lock:
            DBMS._commit_session_impl(session)
            
    @staticmethod
    def _commit_session_impl(session):
        try:
            session.commit()
        except:
            session.rollback()
            raise
