<%inherit file="base.mako"/>
<%def name="title()">Wiki</%def>
<%def name="content()">
<div mod-meta='{"tpl": "project/base.mako", "replace": true}'></div>

<div>

    <div style="width:200px; float:right; margin-left:30px;">

        <div mod-meta='{
                "tpl": "project/wiki/status.mako",
                "replace": true
            }'></div>
        <div mod-meta='{
                "tpl": "project/wiki/nav.mako",
                "replace": true
            }'></div>
        <div mod-meta='{
                "tpl": "project/wiki/toc.mako",
                "replace": true
            }'></div>

    </div>

    ${wiki_content}

</div>

##<div mod-meta='{
##        "tpl": "metadata/knockout.mako",
##        "replace": true
##    }'></div>
##
##
##<div mod-meta='{
##        "tpl": "metadata/comment_group.mako",
##        "kwargs": {
##            "guid": "${wiki_id}",
##            "top": true
##        },
##        "replace": true
##    }'></div>

</%def>