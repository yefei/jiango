# -*- coding: utf-8 -*-
# Created on 2015-9-1
# @author: Yefei
# @version: $Id:$
import sys
import getpass
from django.core.management.base import BaseCommand
from django.core import exceptions
from jiango.admin.models import User, get_password_digest


class Command(BaseCommand):
    help = 'Used to create a admin superuser'

    def handle(self, *args, **options):
        username = None
        password = None
        username_field = User._meta.get_field('username')
        
        try:
            # Get a username
            while username is None:
                if not username:
                    raw_value = raw_input('Username: ')
                
                try:
                    username = username_field.clean(raw_value, None)
                except exceptions.ValidationError as e:
                    self.stderr.write("Error: %s" % '; '.join(e.messages))
                    username = None
                    continue
                
                if User.objects.filter(username=username).exists():
                    self.stderr.write("Error: That username is already taken.")
                    username = None
            
            # Get a password
            while password is None:
                if not password:
                    password = getpass.getpass()
                    password2 = getpass.getpass('Password (again): ')
                    if password != password2:
                        self.stderr.write("Error: Your passwords didn't match.")
                        password = None
                        continue
                if password.strip() == '':
                    self.stderr.write("Error: Blank passwords aren't allowed.")
                    password = None
                    continue

        except KeyboardInterrupt:
            self.stderr.write("\nOperation cancelled.")
            sys.exit(1)
        
        User.objects.create(username=username, password_digest=get_password_digest(password),
                            is_active=True, is_superuser=True)
        self.stdout.write("Admin superuser created successfully.")
