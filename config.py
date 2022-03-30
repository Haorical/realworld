class Config(object):
    SECRET_KEY = '1+1=2'
    JWT_SECRET_KEY = "1+1=4"
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@localhost:3307/flask'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
