### Included where the LogsViewModel is used ###
<div id="logProgressBar" class="progress progress-striped active">
  <div class="progress-bar"  role="progressbar" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width: 100%">
    <span class="sr-only">Loading</span>
  </div>
</div>
<p class="help-block" data-bind="if:tzname">
    All times displayed at
    <span data-bind="text:tzname"></span>
    <a href="http://en.wikipedia.org/wiki/Coordinated_Universal_Time" target="_blank">UTC</a> offset.
</p>
 <dl class="dl-horizontal activity-log"
    data-bind="foreach: {data: logs, as: 'log'}">
    <dt><span class="date log-date" data-bind="text: log.date.local, tooltip: {title: log.date.utc}"></span></dt>
  <dd class="log-content">
    <a data-bind="text: log.userFullName || log.apiKey, attr: {href: log.userURL}"></a>
    <!-- log actions are the same as their template name -->
    <span data-bind="template: {name: log.action, data: log}"></span>
  </dd>
</dl><!-- end foreach logs -->
<%include file="log_templates.mako"/>
