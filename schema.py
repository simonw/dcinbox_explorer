from elasticsearch_dsl import DocType, Completion
from elasticsearch_dsl.field import (
    String, Date as ESDate, Float, Boolean
)
from elasticsearch_dsl import FacetedSearch
from elasticsearch_dsl import TermsFacet, DateHistogramFacet
from elasticsearch_dsl.query import Q
from six import itervalues
import collections


class Email(DocType):
    # {u'Address': u'bernie_sanders@sanders.enews.senate.gov',
    Address = String(index='not_analyzed')
    # u'Body': u' ---------------------- footnotes ---------------------- ',
    Body = String(analyzer='snowball')
    # u'Date': u'08/01/2015',
    Date = ESDate()
    # SKIP: u'Month': u'08',
    # u'Name': u'Senator Bernie Sanders',
    # Confusing since there's also a 'name' field
    Name = String(index='not_analyzed')
    x_name_suggest = Completion()
    # u'Subject': u'Bernie Buzz: Fight for $15!',
    Subject = String(analyzer='snowball')
    # SKIP: u'Year': u'2015',
    # u'alignment': u'Align',
    alignment = String(index='not_analyzed')
    # u'bioguideid': u'S000033',
    bioguideid = String(index='not_analyzed')
    # u'birthday': u'1941-09-08',
    birthday = ESDate()
    # u'caucus': u'Democrat',
    caucus = String(index='not_analyzed')
    # u'congress_numbers': [113, 114, 115],
    congress_numbers = String(index='not_analyzed', multi=True)
    # u'cspanid': 994,
    cspanid = String(index='not_analyzed')
    # u'current': True,
    current = Boolean()
    # u'description': u'Junior Senator from Vermont',
    description = String(analyzer='snowball')
    # u'district': None,
    district = String(index='not_analyzed')
    # u'enddate': u'2019-01-03',
    enddate = ESDate()
    # u'firstname': u'Bernard',
    firstname = String(analyzer='snowball')
    # u'gender': u'male',
    gender = String(index='not_analyzed')
    # SKIP: u'gender_label': u'Male',
    # u'id': 400357,
    id = String(index='not_analyzed')
    # u'lastname': u'Sanders',
    lastname = String(analyzer='snowball')
    # u'leadership_title': None,
    leadership_title = String(analyzer='snowball')
    # u'link': u'https://www.govtrack.us/congress/members/bernard_sanders/400357',
    link = String(index='not_analyzed')
    # u'middlename': u'',
    middlename = String(analyzer='snowball')
    # u'name': u'Sen. Bernard \u201cBernie\u201d Sanders [I-VT]',
    name = String(index='not_analyzed')
    # u'namemod': u'',
    namemod = String(index='not_analyzed')
    # u'nickname': u'Bernie',
    nickname = String(analyzer='snowball')
    # u'osid': u'N00000528',
    osid = String(index='not_analyzed')
    # u'party': u'Independent',
    party = String(index='not_analyzed')
    # u'phone': u'202-224-5141',
    phone = String(index='not_analyzed')
    # u'polarity': u'None',
    polarity = Float()
    # u'pvsid': u'27110',
    pvsid = String(index='not_analyzed')
    # u'role_type': u'senator',
    role_type = String(index='not_analyzed')
    # SKIP: u'role_type_label': u'Senator',
    # u'senator_class': u'class1',
    senator_class = String(index='not_analyzed')
    # SKIP: u'senator_class_label': u'Class 1',
    # u'senator_rank': u'junior',
    senator_rank = String(index='not_analyzed')
    # SKIP: u'senator_rank_label': u'Junior',
    senator_rank_label = String(index='not_analyzed')
    # u'sortname': u'Sanders, Bernard \u201cBernie\u201d (Sen.) [I-VT]',
    sortname = String(index='not_analyzed')
    # u'startdate': u'2013-01-03',
    startdate = ESDate()
    # u'state': u'VT',
    state = String(index='not_analyzed')
    # u'title': u'Sen.',
    title = String(index='not_analyzed')
    # u'title_long': u'Senator',
    title_long = String(analyzer='snowball')
    # u'twitterid': u'SenSanders',
    twitterid = String(index='not_analyzed')
    # u'website': u'http://www.sanders.senate.gov',
    website = String(index='not_analyzed')
    # u'youtubeid': u'senatorsanders'}
    youtubeid = String(index='not_analyzed')

    class Meta:
        index = 'emails'

    def save(self, **kwargs):
        return super(Email, self).save(** kwargs)

    @classmethod
    def properties(cls):
        return [
            prop for prop in
            Email._doc_type.mapping.properties.to_dict(
            )['email']['properties'].keys()
            if not prop.startswith('x_')
        ]


class EmailSearch(FacetedSearch):
    doc_types = [Email]
    # fields that should be searched
    fields = ['Subject', 'Body', 'Name']

    facets = collections.OrderedDict((
        # use bucket aggregations to define facets
        ('gender', TermsFacet(field='gender')),
        ('party', TermsFacet(field='party')),
        ('role_type', TermsFacet(field='role_type')),
        ('state', TermsFacet(field='state', size=60)),
        ('name', TermsFacet(field='name', size=50)),
        ('publish_month', DateHistogramFacet(field='Date', interval='month')),
    ))

    def filter(self, search):
        """
        Over-ride default behaviour (which uses post_filter)
        to use filter instead.
        """
        filters = Q('match_all')
        for f in itervalues(self._filters):
            filters &= f
        return search.filter(filters)

    def query(self, search, query):
        """Overriden to use bool AND by default"""
        if query:
            return search.query('multi_match',
                fields=self.fields,
                query=query,
                operator='and'
            ).sort('-Date')
        return search
