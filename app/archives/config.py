import os, binascii

basedir = os.path.abspath(os.path.dirname(__file__))
class BaseConfig(object):
    UPLOAD_FOLDER = '/clue/static/src'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    SECRET_KEY = binascii.hexlify(os.urandom(24))
    DEBUG=True
    ENV="development"
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'users.db')
    # or 'sqlite:/// + global path to db