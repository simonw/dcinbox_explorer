from elasticsearch.helpers import bulk
from schema import Email
import json
import hashlib
import urllib
from es_connection import connections


def bulk_index(docs):
    return bulk(connections.get_connection('default'),
        (d.to_dict(include_meta=True) for d in docs)
    )


def import_emails(emails, batch_size=100):
    # We go batch_size at a time
    collected = []
    for email in emails:
        collected.append(email)
        if len(collected) == batch_size:
            print bulk_index(email_to_doc(email) for email in collected)
            collected = []
    if collected:
        bulk_index(email_to_doc(email) for email in collected)


def email_to_doc(data):
    # data is a JSON dictionary, returns Email() instance
    kwargs = {}
    for prop in Email.properties():
        kwargs[prop] = data.get(prop) or None
    if kwargs['polarity'] == 'None':
        kwargs['polarity'] = None
    kwargs['x_name_suggest'] = data['Name']
    # We need to derive a unique ID for this email
    # since there's no unique 'id' field (the 'id'
    # field on the doc is actually a congresscritter
    # id) we use an md5 hash of the JSON repr instead
    id = hashlib.md5(json.dumps(data, sort_keys=True)).hexdigest()
    return Email(meta={'id': id}, **kwargs)


def import_all_emails(filename='dataset.json'):
    if filename.startswith('http://') or filename.startswith('https://'):
        fp = urllib.urlopen(filename)
    else:
        fp = open(filename)
    d = json.load(fp)
    import_emails(d)


if __name__ == '__main__':
    import sys
    import_all_emails(sys.argv[-1])
