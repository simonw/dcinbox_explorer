from elasticsearch_dsl.connections import connections
import os

connections.create_connection(hosts=[{
    'host': os.environ['ELASTICSEARCH_HOST'],
    'port': os.environ['ELASTICSEARCH_PORT'],
    'use_ssl': True,
    'http_auth': os.environ['ELASTICSEARCH_AUTH'],
}])
