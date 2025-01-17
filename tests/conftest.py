import os
import tempfile

import pytest
from newspress import create_app
from newspress.database import get_database, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')
@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })
    with app.app_context():
        init_db()
        get_database().executescript(_data_sql)
    yield app
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

# Authentication
class AuthActions(object):
    ''' Auth actions '''
    def __init__(self, client):
        self.client = client

    def login(self, username='test', password='test'):
        ''' test the user login'''
        return self.client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        ''' logout'''
        return self.client.get('/auth/logout')

@pytest.fixture
def auth(client):
    ''' The authentication fixture'''
    return AuthActions(client)
