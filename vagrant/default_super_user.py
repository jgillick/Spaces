from django.contrib.auth.models import User
try:
    User.objects.create_superuser('admin', 'admin@localhost', 'password')
    print "Super user created. admin / password"
except IntegrityError:
    print "Super user already exists"
