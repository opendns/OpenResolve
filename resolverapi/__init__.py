import os

from flask import Flask
from flask_restful import Api
from dns.resolver import Resolver
from flask_cors import CORS


dns_resolver = Resolver()


def create_app(config_name):
    app = Flask(__name__)
    if config_name == 'dev':
        app.config.from_object('resolverapi.config.DevelopmentConfig')
    else:
        app.config.from_object('resolverapi.config.BaseConfig')

    # Get nameservers from environment variable or default to OpenDNS resolvers
    if os.environ.get('RESOLVERS'):
        app.config['RESOLVERS'] = [addr.strip() for addr in os.environ.get('RESOLVERS').split(',')]
    # Respond with Access-Control-Allow-Origin headers. Use * to accept all
    if os.environ.get('CORS_ORIGIN'):
        CORS(app, origins=os.environ.get('CORS_ORIGIN'))

    dns_resolver.lifetime = 3.0

    from resolverapi.endpoints import ReverseLookup
    from resolverapi.endpoints import LookupRecordType
    api = Api(app)
    api.add_resource(ReverseLookup, '/reverse/<ip>')
    api.add_resource(LookupRecordType, '/<rdtype>/<domain>')

    @app.route('/')
    def root():
        """Health check. No data returned. Just 200."""
        return '', 200

    return app
