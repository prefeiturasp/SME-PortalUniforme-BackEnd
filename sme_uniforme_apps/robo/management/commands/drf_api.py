import os

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand

"""
This app was created to speed up the creation of api structures.
Author Weslei Souza
E-mail weslei.andrade.souza@gmail.com
"""

APP_NOT_FOUND = 1
MODEL_NOT_FOUND = 2
MODEL_FOUNDED = 3
SERIALIZER_CONTENT = """
from rest_framework import serializers


class {}(serializers.ModelSerializer):
    class Meta:
        model = {}
        fields = '__all__'
"""

VIEWSET_CONTENT = """
from rest_framework import viewsets


class {}(viewsets.ModelViewSet):
    serializer_class = {}
    queryset = {}.objects.all()
    lookup_field = 'uuid'
"""


class Command(BaseCommand):
    help = 'Command to create boiler plate on Rest Framework'

    BaseCommand.tree = []

    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='This name to be used for create serializer and viewset')
        parser.add_argument('app', type=str, help='What app will be created')
        parser.add_argument('model', type=str, help='What model to be used')
        parser.add_argument('url', type=str, help='What url to api')

    def handle(self, *args, **options):
        name = options['name']
        app = options['app']
        model = options['model']
        url = options['url']
        result = self.model_exists(app, model)
        if result == MODEL_NOT_FOUND:
            self.stderr.write(self.style.ERROR('Model {} Not Found'.format(model)))
        elif result == APP_NOT_FOUND:
            self.stderr.write(self.style.ERROR('App {} Not Found or Not Registry'.format(model)))
        else:
            self.stdout.write(self.style.SUCCESS('Serializer: {}Serializer'.format(name.title())))
            self.stdout.write(self.style.SUCCESS('ViewSet: {}ViewSet'.format(name.title())))
            self.stdout.write(self.style.SUCCESS('URL: {}/'.format(url)))
            self.stdout.write(self.style.SUCCESS('Model: {}'.format(model)))
            self.stdout.write(self.style.SUCCESS('APP: {}'.format(app)))
            self.create_api(name=name)

    def model_exists(self, app_name, model_name):
        try:
            application = apps.get_app_config(app_name).get_models()
            for app in application:
                app_tree = str(app).split('.')
                self._clear_list_directory(app_tree)
                if model_name in self.tree[-1]:
                    return MODEL_FOUNDED
            return MODEL_NOT_FOUND
        except OSError:
            return APP_NOT_FOUND

    def create_api(self, **kwargs):
        base_dir = settings.ROOT_DIR
        app_dir = os.path.join(base_dir, self.tree[0], self.tree[1])
        dir_api = self._create_api_directory(app_dir)
        self._create_serializer(dir_api=dir_api, serializer_name=kwargs['name'])
        self._create_viewset(dir_api=dir_api, viewset_name=kwargs['name'])
        print(self.tree)
        print(dir_api)

    def _create_api_directory(self, directory):
        try:
            api_dir = os.path.join(directory, 'api')
            if not os.path.exists(api_dir):
                os.makedirs(str(api_dir))
                with open(os.path.join(api_dir, '__init__.py'), 'wb'):
                    pass
            return api_dir
        except OSError as err:
            self.stderr.write(self.style.ERROR('Error in  trying create directory: {}'.format(str(err))))

    def _create_serializer(self, **kwargs):
        dir_api = kwargs['dir_api']
        model_name = self.tree[-1]
        file_name_serializer = '{}_serializer'.format(kwargs['serializer_name'])
        dir_serializer = os.path.join(dir_api, 'serializers')
        self._create_dir_module(dir_serializer, file_name_serializer)
        try:
            with open(os.path.join(dir_serializer, '{}.py'.format(file_name_serializer)), "w") as file_serializer:
                class_name = file_name_serializer.replace('_', ' ').title().replace(' ', '')
                file_serializer.write(SERIALIZER_CONTENT.format(class_name, model_name))
                return class_name
        except OSError as err:
            self.stderr.write(self.style.ERROR('Error in tryng create serializer file: {}'.format(str(err))))

    def _create_viewset(self, **kwargs):
        dir_api = kwargs['dir_api']
        model_name = self.tree[-1]
        file_name_viewset = '{}_viewset'.format(kwargs['viewset_name'])
        dir_viewset = os.path.join(dir_api, 'viewsets')
        self._create_dir_module(dir_viewset, file_name_viewset)
        try:
            with open(os.path.join(dir_viewset, '{}.py'.format(file_name_viewset)), "w") as file_viewset:
                class_name = file_name_viewset.replace('_', ' ').title().replace(' ', '')
                file_viewset.write(
                    VIEWSET_CONTENT.format(class_name, '{}Serializer'.format(model_name), model_name))
                return class_name
        except OSError as err:
            self.stderr.write(self.style.ERROR('Error in tryng create viewset file: {}'.format(str(err))))

    def _clear_list_directory(self, tree):
        self.tree = list(map(lambda x: str(x).replace("'", '').replace('<class ', '').replace('>', ''), tree))
        return self.tree

    def _create_dir_module(self, name_dir, name_file, content_file=None):
        try:
            items = ['__init__.py', '{}.py'.format(name_file)]
            os.makedirs(name_dir)
            for item in items:
                with open(os.path.join(name_dir, item), 'wb') as f:
                    if content_file is not None:
                        f.write(content_file)
        except OSError as err:
            self.stderr.write(self.style.ERROR('Error in trying create module: {}'.format(str(err))))
