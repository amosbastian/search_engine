from flask import Flask, render_template
import os, sys

app = Flask(__name__)
app.config.from_object('config')

def is_module(path):
    init_path = os.path.join(path, '__init__.py')

    if os.path.isdir(path) and os.path.exists(init_path):
        return True
    elif os.path.isfile(path) and os.path.splitext(path)[1] == '.py':
        return True

    return False

def import_module(name, globals=globals(), locals=locals(), 
    fromlist=[], level=-1):
    __import__(name)

    return sys.modules[name]

def register_views(app, path, extension=''):
    """
    Import all the blueprints by searching for the blueprint variable 
    in all the files in the given directory path.
    """
    app_path = os.path.dirname(os.path.abspath(app.root_path))

    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        # Check if the current file is a module.
        if is_module(file_path):
            # Get the module name from the file path.
            module_name = os.path.splitext(file_path)[0]
            module_name = os.path.relpath(module_name, app_path)
            module_name = module_name.replace('/', '.')
            blueprint   = getattr(import_module(module_name), 'blueprint', None)
            
            if blueprint:
                app.register_blueprint(blueprint)

path = os.path.dirname(os.path.abspath(__file__))
register_views(app, os.path.join(path, 'views'))