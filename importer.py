from elasticsearch.helpers import streaming_bulk
from schema import Email
import json
import hashlib
import urllib
from es_connection import connections


def import_emails(emails):
    done = 0
    for report in streaming_bulk(connections.get_connection('default'), (
        email_to_doc(email).to_dict(include_meta=True)
        for email in emails
    )):
        done += 1
        if done % 500 == 0:
            print "Done %d" % done


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
        print "Downloading %s... (this may take a few minutes)" % filename
        fp = urllib.urlopen(filename)
    else:
        fp = open(filename)
    d = json.load(fp)
    import_emails(d)


if __name__ == '__main__':
    import sys
    import_all_emails(sys.argv[-1])
