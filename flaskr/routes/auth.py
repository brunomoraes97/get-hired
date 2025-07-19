from flask import Blueprint, request, jsonify, current_app, make_response, render_template
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta

routes_auth = Blueprint('auth', __name__, url_prefix='/auth')


def get_supabase():
    if not hasattr(current_app, 'supabase'):
        url = current_app.config.get('SUPABASE_URL')
        key = current_app.config.get('SUPABASE_KEY')
        if not url or not key:
            raise RuntimeError('Supabase credentials not configured')
        from supabase import create_client
        current_app.supabase = create_client(url, key)
    return current_app.supabase


@routes_auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Invalid data'}), 400
    email = data['email']
    password = generate_password_hash(data['password'])
    profile = {
        'email': email,
        'password': password,
        'name': data.get('name', '')
    }
    supabase = get_supabase()
    supabase.table('users').insert(profile).execute()
    return jsonify({'status': 'registered'})


@routes_auth.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')


@routes_auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Invalid data'}), 400
    supabase = get_supabase()
    res = supabase.table('users').select('*').eq('email', data['email']).execute()
    user = res.data[0] if res.data else None
    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    token = jwt.encode({'sub': user['email'],
                        'exp': datetime.utcnow() + timedelta(hours=8)},
                       current_app.config['JWT_SECRET'], algorithm='HS256')
    resp = make_response({'status': 'logged_in'})
    resp.set_cookie('token', token, httponly=True, samesite='Lax')
    return resp


@routes_auth.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')


@routes_auth.route('/logout', methods=['POST'])
def logout():
    resp = make_response({'status': 'logged_out'})
    resp.delete_cookie('token')
    return resp

