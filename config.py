class Config:
    DEBUG = True
    TEMPLATES_RELOAD = True
    SECRET_KEY = 'secret_xxx'
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/taskscheduler.sqlite'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
