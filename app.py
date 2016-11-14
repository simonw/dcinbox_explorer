from flask import Flask, render_template, request, Response
from schema import EmailSearch, Email
import es_connection
import json
import urllib
import datetime


app = Flask(__name__)


@app.route("/")
def homepage():
    q = request.args.get('q', '') or None

    whitelisted_facet_args = {}
    for key, value in request.args.items():
        if key in EmailSearch.facets:
            whitelisted_facet_args[key] = facet_to_filter(key, value)

    es = EmailSearch(query=q, filters=whitelisted_facet_args)
    es = es[:20]
    response = es.execute()
    facets = response.facets
    # Hack to order them by the order defined in EmailSearch.facets
    facets = [(key, value) for key, value in facets._d_.items()]
    facets.sort(key=lambda p: EmailSearch.facets.keys().index(p[0]))
    facet_dicts = []
    for facet_name, values in facets:
        facet_values = []
        for value, count, selected in values:
            value = convert_facet_value(facet_name, value)
            if selected:
                href = href_with_removed(facet_name, value)
            else:
                href = href_with_added(facet_name, value)
            facet_values.append({
                'value': value,
                'count': count,
                'selected': selected,
                'href': href,
            })
        d = {
            'name': facet_name,
            'vals': facet_values,
        }
        facet_dicts.append(d)
    return render_template('homepage.html', **{
        'args': request.args,
        'total': response.hits.total,
        'docs': list(response),
        'facets': facet_dicts,
        'q': q or ''
    })


@app.route("/email/<id>/")
def email(id):
    doc = Email.get(id=id)
    return render_template('email.html', **{
        'email': doc,
        'as_json': json.dumps(dict(doc.__dict__['_d_']), indent=4, default=lambda x: unicode(x)),
    })


@app.route("/robots.txt")
def robots_txt():
    return Response("""User-agent: *
Disallow: /
""", mimetype='text/plain')


def href_with_removed(key, value):
    existing = dict(request.args.iteritems())
    for key, value in existing.items():
        existing[key] = value.encode('utf8')
    if key in existing:
        del existing[key]
    return '/?' + urllib.urlencode(existing)


def href_with_added(key, value):
    existing = dict(request.args.iteritems())
    existing[key] = value
    for key, value in existing.items():
        existing[key] = value.encode('utf8')
    return '/?' + urllib.urlencode(existing)


def convert_facet_value(facet_name, value):
    if facet_name == 'publish_month':
        return value.strftime('%Y-%m')
    return value


def facet_to_filter(facet_name, value):
    if facet_name == 'publish_month':
        yyyy, mm = map(int, value.split('-'))
        return datetime.datetime(yyyy, mm, 1, 0, 0, 0)
    return value


if __name__ == "__main__":
    app.run()
