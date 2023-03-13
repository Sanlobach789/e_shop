import os

from django.core.management import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            apps = ['adminapp', 'authapp', 'basketapp', 'mainapp', 'ordersapp']
            for app in apps:
                migrations_folder = os.path.join(os.getcwd(), app, 'migrations')
                if os.path.exists(migrations_folder):
                    files = os.listdir(migrations_folder)
                    init_index = files.index('__init__.py')
                    files.pop(init_index)
                    for file in files:
                        file_path = os.path.join(migrations_folder, file)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
        except OSError as e:
            print(e)
