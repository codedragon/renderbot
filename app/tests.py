import app.__init__ as app_init
from app.__init__ import db
from app.auth.forms import RegistrationForm
from app.models import User
from app.auth.uploads import file_validate as fv
from config import app_config
from flask import Flask
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_testing import TestCase
from flask.ext.login import current_user
import os
import pytest
import tempfile
import unittest

# to test, run: $python3 -m unittest discover
# or run: $python3 -m pytest tests.py
# NB: before testing, you must run:
# $export FLASK_APP=run.py
# $export FLASK_CONFIG=development
# contexts in flask: http://kronosapiens.github.io/blog/2014/08/14/understanding-contexts-in-flask.html
# https://pythonhosted.org/Flask-Testing/

class RenderbotTestCase(TestCase):
    # Testing setup
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True

    def create_app(self):
        app = app_init.create_app('testing')
        app.config['TESTING'] = True # not sure I need this
        return app

    def setUp(self):
        self.c = self.app.test_client()
        db.init_app(self.app)
        # db.create_all(app=app_init.create_app('testing'))
        db.create_all()
        self.first_user =  User(email="test@test.com",
                        username="Test",
                        first_name="Tom",
                        last_name="Test",
                        password="test")
        self.second_user =  User(email="tomtest@test.com",
                        username="TomTest",
                        first_name="Tom",
                        last_name="Test",
                        password="test")
        self.duplicate_user =  User(email="test@test.com",
                        username="Test2",
                        first_name="Tom2",
                        last_name="Test",
                        password="test")
        db.session.add(self.first_user)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def login(self, email, password):
        return self.c.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.test_client().get('/logout', follow_redirects=True)

    # tests of individual pages

    def test_home_dir(self):
        rv = self.c.get('/')
        assert b'Renderbot' in rv.data

    # test dashboard while not logged in
    def test_unverified_dashboard(self):
        rv = self.c.get('/dashboard', follow_redirects=True)
        assert b'You must be logged in to access this page.' in rv.data

    def test_registration_page(self):
        rv = self.c.get('/register')
        assert b'Register for an Account' in rv.data

    def test_login_pate(self):
        rv = self.c.get('/login')
        assert b'Login to your account' in rv.data

    # def test_login(self):
    #     with self.c:
    #         rv = self.c.post('/login', data=dict(
    #             email="test@test.com",
    #             password="test"
    #         ), follow_redirects=True)
    #         print(rv.data)
    #         # assert b'Hi,' in rv.data
    #         # print(current_user)
    #         self.assert_redirects(rv, url_for('home.dashboard'))

    # def test_logout(self):
    #     rv = self.logout()
    #     assert b'You have successfully been logged out.' in rv.data

    # def test_login(self):
    #     rv = self.login('test@test.com', 'test')
    #     assert b'Hi,' in rv.data
    #     print(rv.data)
    #     rv = self.login('bob', 'joe')
    #     assert b'Invalid email address.' in rv.data
    #     rv = self.login('test@test.com', 'fake')
    #     print(rv.data)
    #     assert b'Invalid email or password.' in rv.data

    # test rendering of form submissions

    # def test_registration_form(self):
    #     # for problems here: http://stackoverflow.com/questions/17375340/testing-code-that-requires-a-flask-app-or-request-context
    #     with self.app.app_context():
    #         r = RegistrationForm()

    # unit tests

    # test that database is set up properly
    def test_db_set_up(self):
        assert self.first_user in db.session

    # test database interaction
    def test_db_user_creation(self):
        db.session.add(self.second_user)
        assert self.second_user in db.session

    def test_incorrect_user(self):
        assert self.duplicate_user not in db.session

    def test_file_open(self):
        with open('auth/uploads/test.txt', 'r') as f:
            r = f.read()
        print(os.getcwd())
        assert 'test' in r

if __name__ == '__main__':
    unittest.main()
