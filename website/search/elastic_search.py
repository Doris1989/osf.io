from website import settings
import logging
import pyelasticsearch
import collections

logger = logging.getLogger(__name__)

if settings.SEARCH_ENGINE in ["elastic", "all"]:
    try:
        elastic = pyelasticsearch.ElasticSearch("http://localhost:9201")
        logging.getLogger('pyelasticsearch').setLevel(logging.DEBUG)
        logging.getLogger('requests').setLevel(logging.DEBUG)
    except Exception as e:
        logger.error(e)
        logger.warn("The SEARCH_ENGINE setting is set to 'elastic', but there"
                "was a problem starting the elasticsearch interface. Is "
                "elasticsearch running?")
        elastic=None
else:
    elastic=None
    logger.warn("Elastic is not set to start")
        

def search(raw_query, start=0):

    # Converts unicode dictionary to utf-8 dictionary
    def convert(data):
        if isinstance(data, basestring):
            return str(data)
        elif isinstance(data, collections.Mapping):
            return dict(map(convert, data.iteritems()))
        elif isinstance(data, collections.Iterable):
            return type(data)(map(convert, data))
        else:
            return data
#    raw_query = raw_query.split(":")
#    raw_query_dict = dict()
#    i = 0
#    while i < len(raw_query)-1:
#        raw_query_dict[raw_query[i]] = raw_query[i+1]
#        i+=1

    query = {
        'query': {
            'match' : {
                '_all': raw_query
            }
        }
    }
    raw_results = convert(elastic.search(query, index='website'))
    results = {
            'start':0, 
            'numFound':raw_results['hits']['total'], 
            'docs':[hit['_source'] for hit in raw_results['hits']['hits']]
    }
#    return results, [], []
    return create_result(results['docs']), results['numFound']#TODO(fabianvf)


def update_node(node):
    from website.addons.wiki.model import NodeWikiPage

    if not (settings.SEARCH_ENGINE in ['elastic', 'all']):
        return

    if node.category =='project':
        elastic_document_id = node._id
        category = node.category
    else:
        try:
            elastic_document_id = node.parent_id
            category = 'component'
        except IndexError:
            # Skip orphaned components
            return
    if node.is_deleted or not node.is_public:
        delete_doc(elastic_document_id, node)
    else:
        elastic_document = {
            'id': elastic_document_id,
            'contributors': [
                x.fullname for x in node.contributors
                if x is not None
            ],
            'contributors_url': [
                x.profile_url for x in node.contributors
                if x is not None
            ],
            'title': node.title,
            'category': node.category,
            'public': node.is_public,
            'tags': [x._id for x in node.tags],
            'description': node.description,
            'url': node.url,
            'registeredproject': node.is_registration,
        }
        for wiki in [
            NodeWikiPage.load(x)
            for x in node.wiki_pages_current.values()
        ]:
            elastic_document.update({
                '__'.join((node._id, wiki.page_name, 'wiki')): wiki.raw_text
            })
        # check to see if the document is in the elasticsearch database
#        try: #TODO(fabianvf)
#            new = solr.query(id=solr_document['id']).execute()[0]
#            new = elastic.search(query={
#                "query":{
#                    "match" : {
#                        "id": elastic_document['id']
#                        }
#                    }
#                })
#            logger.warn(new)
#            x = raw_input()
#        except IndexError:
#           new = dict()

#        if elastic_document:
#            new.update(clean_solr_doc(solr_document))

        elastic.index('website', category, elastic_document, elastic_document_id)


def update_user(user):
    elastic.index("website", "user",{
        'id' : user._id, 
        'user' : user.fullname
        })

def delete_all():
    elastic.delete_all('website', 'project')
    elastic.delete_all('website', 'user')
    elastic.delete_all('website', 'component')

def delete_doc(elastic_document_id, node):
    if node.category == 'project':
        category = 'project'
    else:
        category = 'component'
    try:
        elastic.delete('website', category, elastic_document_id) 
    except pyelasticsearch.exceptions.ElasticHttpNotFoundError:
        logger.warn("Document with id {} not found in database".format(elastic_document_id))

def create_result(results):
    logger.warn(str(results))
    result_search = []
    tags = {}
    for result in results:
        container = {}
        doc_id = result['id']
        # users are separate documents in our search database,
        # so the logic for returning
        # those documents is different
        if 'user' in result:
            container['user'] = result['user']
            container['user_url'] = '/profile/'+result['id']
            result_search.append(container)
        else:
            container['title'] = result.get('title', '-- private project --')
            container['url'] = result.get('url')
            contributors = []
            contributors_url = []
            # we're only going to show contributors on projects, for now
            for contributor in result.get('contributors', []):
                contributors.append(contributor)
            for url in result.get('contributors_url',[]):
                contributors_url.append(url)
            container['contributors'] = contributors
            container['contributors_url'] = contributors_url
            # highlights will be returned as liss
            main_lit = []
            # we will create the wiki links
            main_wiki_link = ''
            # nest is for our nested nodes; i.e, materials, procedure ects
            nest = {}
            component_tags = []
            # need to keep track of visisted nodes for our tag cloud so we dont
            # miscount our fx of tags
            visited_nests = []
#            for key, value in highlights[id].iteritems(): #TODO(fabianvf)
#                if id in key:
                    # if wiki is in the key,
                    # we have to split on __ to build the url for the wik
#                    if '__wiki' in key:
#                        main_wiki_link = result[id+'_url'] + (
#                           '/wiki/' + key.split('__')[1])
                    # we're only going to show
                    # the highlight if its wiki or description. title or
                    # tags is redundant information
#                    if '__wiki' in key or '_description' in key:
#                        main_lit = value
                # if id is not in key, we know that we have some
                # nested information to display
#                elif id not in key:
#                    if key == 'id':
#                        continue
                    # our first step is to get id of the
                    # node by splitting the key
                    # wiki keys are set up to include page name as well.
                    # so splitting to find
                    # the node id is different
#                    if '__wiki' in key:
#                        splits = key.split('__')
#                        split_id = splits[0]
#                        pagename = splits[1]
#                    else:
#                        split_id = key.split('_')[0]
                    # nodes can have contributors
#                    contributors = []
#                    contributors_url = []
#                    lit = []
#                    wiki_link = ''
                    # build our wiki link
#                    if '__wiki' in key:
#                        wiki_link = result[split_id+'_url'] + '/wiki/'+pagename
                    # again title and tags are
                    # redundant so only show highlight if the
                    # wiki or description are in the key
#                    if '__wiki' in key or '_description' in key:
#                        if value[0] != 'None':
#                            lit = value
                    # build our contributor list and our contributor url list
#                    for contributor in result.get(split_id+'_contributors', []):
#                        contributors.append(contributor)
#                    for url in result.get(split_id+'_contributors_url', []):
#                        contributors_url.append(url)
#                    if result[split_id+'_public']:
#                        nest[split_id] = {
#                            'title': result[split_id+'_title'],
#                            'url': result[split_id+'_url'],
#                            'highlight': lit or nest.get(split_id)['highlight'] if nest.get(split_id) else None,
#                            'wiki_link': wiki_link,
#                            'contributors': contributors,
#                            'contributors_url': contributors_url
#                        }
#                        if split_id+'_tags' in result:
#                            if split_id not in visited_nests:
                                # we've visted the node so
                                # append to our visited nests lists
#                                visited_nests.append(split_id)
                                # we're going to have a
                                # list of all tags for each project.
                                # we're creating a list with no
                                # duplicates using sets
#                                component_tags = component_tags + list(
#                                    set(result[split_id+'_tags']) - set(
#                                        component_tags))
                                # count the occurence of each tag
#                                for tag in result[split_id+'_tags']:
#                                    if tag not in tags.keys():
#                                        tags[tag] = 1
#                                    else:
#                                        tags[tag] += 1
            # add the highlight to our dictionary
            container['highlight'] = []
            if main_lit:
                container['highlight'] = main_lit
#            else:
                container['highlight'] = None
            # and the link to the wiki
            container['wiki_link'] = main_wiki_link
            # and our nested information
            container['nest'] = nest
            container['is_registration'] = result.get(
                'registeredproject',
                False
            )
            if 'tags' in result.keys():
                # again using sets to create a list without duplicates
                container['tags'] = result['tags'] + list(
                    set(component_tags) - set(result['tags']))
                # and were still keeping count of tag occurence
                for tag in result['tags']:
                    if tag not in tags.keys():
                        tags[tag] = 1
                    else:
                        tags[tag] += 1
            result_search.append(container)
    return result_search, tags


def search_contributor():
    raise NotImplementedError
