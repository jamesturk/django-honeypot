DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}
INSTALLED_APPS = ('honeypot',)
SECRET_KEY = 'honeyisfrombees'
