# Copyright (C) 2017-2019 Max R.D. Parmer
# License AGPLv3+: GNU Affero GPL version 3 or later.
# http://www.gnu.org/licenses/agpl.html

import requests

from .casefile import load_case

DEFAULT_STRUCT = {'fields': {
    'project': {'key': ''},
    'summary': '',
    'description': '',
    'issuetype': {'name': ''},
}}


def prep_case(case, conf):
    try:
        summary, details = load_case(case, conf)
        if ': ' in summary:
            summary_less_timestamp = summary.partition(': ')[2].strip()
            summary = f'{case} {summary_less_timestamp}'
        else:
            summary = f'{case} {summary}'
    except FileNotFoundError as missing_file:
        print(f'The case "{case}" does not exist or is missing the '
              f'expected notes file "{missing_file}"')

    return (summary, details)


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
