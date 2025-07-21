import os
from werkzeug.security import generate_password_hash
from supabase import create_client

url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_KEY')
if not url or not key:
    raise SystemExit('Supabase credentials not configured')

supabase = create_client(url, key)

fake = {
    'email': 'test@example.com',
    'password': generate_password_hash('test123'),
    'name': 'Test User'
}

supabase.table('users').insert(fake).execute()
print('Fake user created')
