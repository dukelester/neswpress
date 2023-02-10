'''' Application factory function '''
import os

from flask import Flask

def create_app(test_config=None):
    ''' Create and configure the application '''
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRETE_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'newspress.sqlite'),
    )
    if test_config is None:
        # load the instance config , if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    # ensure the instance folder exixts
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    # say hello
    @app.route('/hello')
    def hello():
        return '<h3> Hello welcome to our blog and news </h3>'
    return app
