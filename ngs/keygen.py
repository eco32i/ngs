from django.utils.crypto import get_random_string

chars = '1234567890-=!@#$%^&*()_+qwertyuiopasdfghjkl;zxcvbnm,./'

def generate_secret_key(filepath):
    with open(filepath,  'w') as keyfile:
        keyfile.write('SECRET_KEY = %s' % get_random_string(50, chars))
