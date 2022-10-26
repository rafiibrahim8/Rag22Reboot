import datetime
import hashlib
import hmac
import json
import os

class BDT(datetime.tzinfo):
    def utcoffset(self, dt):
        return datetime.timedelta(hours=6)
    def dst(self, dt):
        return datetime.timedelta(hours=6)
    def tzname(self, dt):
        return 'Bangladesh Standard Time'

def sql_all_to_json(objs, sort_by=None):
    if len(objs) < 1:
        return []
    values = list()
    columns = [col.name for col in objs[0].__table__.columns]
    for i in objs:
        val = dict()
        for j in columns:
            val[j] = i.__getattribute__(j)
        values.append(val)
    if sort_by:
        values.sort(key=lambda x: x[sort_by])
    return values

def secure_compare(a, b):
    return hmac.compare_digest(a, b) # prevent timing attack

def read_config(config_file='env.json'):
    with open(config_file, 'r') as f:
        env = json.load(f)
    if not 'flask_secret' in env:
        env['flask_secret'] = hashlib.sha256(os.urandom(2048)).hexdigest()
        with open(config_file,'w') as f:
            json.dump(env, f, indent=4)
    return env

def add_or_append_edits(qr):
    edits = json.loads(qr.edits or '[]')
    new_edit = {
        'epoch': qr.epoch,
        'datetime': qr.datetime,
        'buyer_name': qr.buyer_name,
        'buyer_phone': qr.buyer_phone,
        'amount': qr.amount,
        'seller': qr.seller
    }
    edits.append(new_edit)
    return json.dumps(edits)

def current_bd_datetime_str(format='%Y-%m-%d %H:%M:%S'):
    return datetime.datetime.now(BDT()).strftime(format)
