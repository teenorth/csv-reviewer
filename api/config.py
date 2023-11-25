from decouple import config


class Config:
    '''Configuration class getting each required environment
    variable. Review ".env.example".
    '''
    JWT_SECRET_KEY = config('JWT_SECRET_KEY')
    DB_URL = config('DB_URL')
    ALLOWED_ORIGINS = config('ALLOWED_ORIGINS')
