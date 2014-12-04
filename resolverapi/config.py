class BaseConfig(object):
    DEBUG = False
    RESOLVERS = ['208.67.222.222', '208.67.220.220']
    SUPPORTED_RDTYPES = (
        'A',
        'AAAA',
        'CNAME',
        'LOC',
        'MX',
        'NAPTR',
        'NS',
        'PTR',
        'SOA',
        'TXT'
    )


class DevelopmentConfig(BaseConfig):
    DEBUG = True
