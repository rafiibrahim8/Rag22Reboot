from flask import Flask
from flask import request as f_req

import utils
from middleware import Middleware, RequestValidator

env = utils.read_config()
app = Flask(__name__)

app.config['SECRET_KEY'] = env['flask_secret']
middleware = Middleware(env)

@app.get('/')
def home():
    return 'Hello Satyam', 200


@app.post('/login')
def hangle_login():
    req = f_req.get_json()
    if not RequestValidator.validate(req):
        return {'status': 403}, 403
    return middleware.login(req)


@app.post('/qr_scan')
def handle_qr():
    req = f_req.get_json()
    if not RequestValidator.validate(req, True):
        return {'status': 403}, 403
    return middleware.handle_qr(req)

@app.post('/make_sell')
def mk_sell():
    req = f_req.get_json()
    if not RequestValidator.validate(req, True):
        return {'status': 403}, 403
    return middleware.handle_sell(req)

@app.post('/edit_sell')
def edit_sell():
    req = f_req.get_json()
    if not RequestValidator.validate(req):
        return {'status': 403}, 403
    return middleware.edit_sell(req)

@app.post('/admin_api')
def handle_admin_api():
    auth_header = f_req.headers.get('Authorization')
    if not (auth_header and utils.secure_compare(auth_header.lower(), f'bearer {env["api_token"]}')):
        return 'Forbidden!', 403
    if not f_req.get_json():
        return 'Bad Request!', 400
    return middleware.handle_admin_api(f_req.get_json())

if __name__ == '__main__':
    app.run(port=65014, host='0.0.0.0')
