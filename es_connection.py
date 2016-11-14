from elasticsearch_dsl.connections import connections
import os

connections.create_connection(hosts=[{
    'host': os.environ['ELASTICSEARCH_HOST'],
    'port': os.environ['ELASTICSEARCH_PORT'],
    'use_ssl': bool(os.environ.get('ELASTICSEARCH_USE_SSL')),
    'http_auth': os.environ['ELASTICSEARCH_AUTH'],
}])
