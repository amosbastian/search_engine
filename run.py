#!venv/bin/python
# encoding: utf-8
from flask_failsafe import failsafe

@failsafe
def create_app():
    from app import app

    return app

if __name__ == '__main__':
    create_app().run(debug=True, port=5555)