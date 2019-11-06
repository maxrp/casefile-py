# Copyright (C) 2017-2019 Max R.D. Parmer
# License AGPLv3+: GNU Affero GPL version 3 or later.
# http://www.gnu.org/licenses/agpl.html

import requests

DEFAULT_STRUCT = {'fields': {
    'project': {'key': ''},
    'summary': '',
    'description': '',
    'issuetype': {'name': ''},
}}


def jira_post(summary, description, conf):
    post_data = DEFAULT_STRUCT.copy()
    post_data['fields']['summary'] = summary
    post_data['fields']['description'] = description
    post_data['fields']['project']['key'] = conf['jira_proj']
    post_data['fields']['issuetype']['name'] = 'Incident'

    url = f'https://{conf["jira_domain"]}/rest/api/2/issue/'
    response = requests.post(url, json=post_data, auth=(conf['jira_user'],
                                                        conf['jira_key']))

    if response.status_code == requests.codes.created:
        response = response.json()
        print('Case promoted to issue: '
              f'https://{conf["jira_domain"]}/browse/{response["key"]}')
    else:
        response.raise_for_status()
