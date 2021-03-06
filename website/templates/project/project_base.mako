<%inherit file="../base.mako"/>

<%def name="og_description()">

    %if node['description']:
        ${sanitize.strip_html(node['description']) + ' | '}
    %endif
    Hosted on the Open Science Framework


</%def>

<%def name="content()">

<%include file="project_header.mako"/>
<%include file="modal_show_links.mako"/>

${next.body()}

% if node['node_type'] == 'project':
    <%include file="modal_duplicate.mako"/>
% endif

</%def>

<%def name="javascript_bottom()">

<script>

    <% import json %>
    ## TODO: Move this logic into badges add-on
    % if 'badges' in addons_enabled and badges and badges['can_award']:
    ## TODO: port to commonjs
    ## $script(['/static/addons/badges/badge-awarder.js'], function() {
    ##     attachDropDown('${'{}badges/json/'.format(user_api_url)}');
    ## });
    % endif

    var nodeId = '${node['id']}';
    var userApiUrl = '${user_api_url}';
    var nodeApiUrl = '${node['api_url']}';
    // Mako variables accessible globally
    window.contextVars = $.extend(true, {}, window.contextVars, {
        currentUser: {
            ## TODO: Abstract me
            username: ${json.dumps(user['username']) | n},
            id: '${user_id}',
            urls: {api: userApiUrl},
            isContributor: ${json.dumps(user.get('is_contributor', False))},
            fullname: ${json.dumps(user['fullname']) | n}
        },
        node: {
            ## TODO: Abstract me
            id: nodeId,
            title: ${json.dumps(node['title']) | n},
            urls: {api: nodeApiUrl},
            isPublic: ${json.dumps(node.get('is_public', False))},
            piwikSiteID: ${json.dumps(node.get('piwik_site_id', None))},
            piwikHost: ${json.dumps(piwik_host)}
        }
    });

</script>
## NOTE: window.contextVars must be set before loading this script
<script src="/static/public/js/project-base-page.js"> </script>
</%def>
