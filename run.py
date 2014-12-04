import os
from resolverapi import create_app

app = create_app(os.environ.get('RESOLVER_ENV', 'prod'))

if __name__ == '__main__':
    app.run()
