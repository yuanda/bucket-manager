import urllib
from httplib import BadStatusLine

from time import sleep


from xml.etree import ElementTree
from collections import OrderedDict
# import gevent
# from gevent import monkey ; monkey.patch_all(socket = False)

import SPARQLWrapper

from . import config

from simplejson.decoder import JSONDecodeError

RESOURCE_PREFIX = "http://dbpedia.org/resource/"

def build_query(resource="The_Sopranos", limit=1,
        ordering='asc', order_by='outward'):
    """Given node, return each neighbor node with a count of all nodes the
    neighbor is pointing to and another count of all nodes pointing to the
    neighbor.

    order_by the count of nodes pointing 'outward' from or 'inward' to neighbor
    """
    order_by_first = "?count_outward_nodes"
    order_by_second = "?count_inward_nodes"
    if order_by != "outward":
        _tmp = order_by_first
        order_by_first = order_by_second
        order_by_second = _tmp
    query = """
prefix dcterms: <http://purl.org/dc/terms/>
prefix dbpedia: <http://dbpedia.org/resource/>
SELECT count(?outwardnode) as ?count_outward_nodes
       count(?inwardnode) as ?count_inward_nodes
       ?node
       ?label
where {
    {
        ?node dcterms:subject <%(resource)s> .
        OPTIONAL { ?node rdfs:label ?label } .
    } UNION {
        ?node skos:broader <%(resource)s> .
        OPTIONAL { ?node rdfs:label ?label } .
    } UNION {
        <%(resource)s> dcterms:subject ?node .
        OPTIONAL { ?node rdfs:label ?label } .
    } UNION {
        <%(resource)s> skos:broader ?node .
        OPTIONAL { ?node rdfs:label ?label } .
    }
.
    {
        ?inwardnode dcterms:subject ?node .
    } UNION {
        ?inwardnode skos:broader ?node .
    }
UNION
    {
        ?node dcterms:subject ?outwardnode .
    } UNION {
        ?node skos:broader ?outwardnode .
    }
}
order by %(ordering)s( %(first)s ) %(ordering)s( %(second)s )
limit %(limit)s
    """ % { 'resource':RESOURCE_PREFIX + resource,
            'ordering':ordering,
            'first': order_by_first,
            'second': order_by_second,
            'limit':limit,}
    return query

def download(query, url=config.DBPEDIA_URL):
    sp = SPARQLWrapper.SPARQLWrapper2(url)
    sp.setQuery(query)

    try:
        resp = sp.queryAndConvert()
    except JSONDecodeError:
        return []
    except BadStatusLine:
        return []
    except IOError:
        return []
    except Exception as e:
        print type(e), e.message
        return []

    for x in resp.bindings:
        for key in x.keys():
            if x[key].lang:
                val = [ x[key].value, x[key].lang ]
            else:
                val = x[key].value
            x[key] = val
    return resp.bindings

def clean(data):
    """Combines duplicate nodes with different labels into one structure,
    renames the default keys to more sensible ones,
    general cleanup"""
    cleaned = OrderedDict()
    for elem in data:
        # Uniquify nodes on node url
        key = elem['node']
        # Set keys appropriately
        if key not in cleaned:
            elem['node_url'] = elem['node'] # immutable strings
            elem['node'] = elem['node'].split('/')[-1]
            elem['all_labels'] = [elem.get('label') or [None,None]]
            cleaned[key] = elem
        else:
            cleaned[key]['all_labels'].append( elem['label'] )

    # Set 'label' for each node
    for k in cleaned:
        elem = cleaned[k]
        elem['label'] = elem['all_labels'][0][0] # set default
        for x in elem['all_labels']:
            if x[1] == "en":
                elem['label'] = x[0]
    return cleaned.values()

def find_neighbors(resource="The_Sopranos", limit=1,
        ordering='asc', order_by='outward', url=config.DBPEDIA_URL):
    query = build_query(resource, limit, ordering, order_by)
    data = download(query, url)
    data = clean(data)
    return data

def async_find_neighbors(resources, limit=1,
        ordering='asc', order_by='outward'):
    queue = [gevent.spawn(find_neighbors, resource, limit, ordering, order_by)
                for resource in resources]
    gevent.joinall(queue)
    return [x.get() for x in queue]

def create_resource_names(resources):
    names = []
    for rsc in resources:
        names.append(rsc)
        names.append("Category:" + rsc)
    return names

def create_resource_dict(resource, label = u''):

    default_dict = {}
    default_dict['count_inward_nodes'] = '1'
    default_dict['count_outward_nodes'] = '1'
    default_dict['node'] = resource
    default_dict['node_url'] = ''
    default_dict['all_labels'] = ''
    default_dict['label'] = label

    return default_dict

def extract_resource(uri):
    """
    Extracts the resource name from a DBpedia resource URI.
    """
    
    start = uri.index(RESOURCE_PREFIX) + len(RESOURCE_PREFIX)
    
    return uri[start:]

def dbpedia_lookup(term, base_url):
    """
    Performs a dbpedia term lookup using the specified resource.
    """
    
    url =  base_url
    url += '/search.asmx/KeywordSearch?QueryString='
    url += urllib.quote(term)
    
    while True:
        try:
            src = urllib.urlopen(url)
            break
        except IOError:
            sleep(2)

    tree = ElementTree.fromstring(src.read())
    src.close()
    
    matches = []
    for i, node in enumerate(tree.iter("{http://lookup.dbpedia.org/}Result")):
        uri = node.find("{http://lookup.dbpedia.org/}URI").text
        resource = extract_resource(uri)
        label = node.find("{http://lookup.dbpedia.org/}Label").text
        matches.append(create_resource_dict(resource, label))
        
    return matches


