import os
import json
import subprocess
import urllib
import urllib.request
from urllib.request import urlopen

REPOSITORY_NAME = os.environ['GITHUB_REPOSITORY_OWNER']

GH_TOKEN = os.environ['GITHUB_TOKEN']

GET_ISSUES_URL = 'https://api.github.com/repos/{}/{}/issues'.format(
    REPOSITORY_NAME, 'namada')
CREATE_ISSUE_URL = 'https://api.github.com/repos/{}/{}/issues'.format(
    REPOSITORY_NAME, 'namada')
MODIFY_ISSUE = 'https://api.github.com/repos/{}/{}/issues/{}'.format(
    REPOSITORY_NAME, 'namada', '{}')
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/vnd.github.v3+json',
    'Authorization': 'token {}'.format(GH_TOKEN)
}

ISSUE_TITLE = 'Cargo Udeps'
ISSUE_LABEL = 'dependencies'


def get_nightly_from_file() -> str:
    workspace = os.environ['GITHUB_WORKSPACE']
    return open("{}/rust-nightly-version".format(workspace), "r").read().strip()


# 0 - not exist,2 already exist, else issue number
def check_issue_status(body: str) -> int:
    params = {'creator': 'github-actions[bot]', 'state': 'open'}
    params_encoded = urllib.parse.urlencode(params)
    req = urllib.request.Request("{}?{}".format(
        CREATE_ISSUE_URL, params_encoded), headers=HEADERS)

    with urlopen(req) as response:
        issues = json.load(response)
        for issue in issues:
            title_check = issue['title'] == ISSUE_TITLE
            if title_check:
                if issue['body'] == body:
                    return 2
                return issue['number']
        return 0


def modify_issue(issue_number: int, body: str):
    body = {"body": body}
    encoded_body = json.dumps(body).encode('ascii')
    req = urllib.request.Request(MODIFY_ISSUE.format(
        issue_number), data=encoded_body, headers=HEADERS)
    req.get_method = lambda: 'PATCH'

    with urlopen(req) as response:
        json.load(response)


def create_issue(body: str):
    body = {"title": ISSUE_TITLE, "body": body, "labels": [ISSUE_LABEL]}
    encoded_body = json.dumps(body).encode('ascii')
    req = urllib.request.Request(
        CREATE_ISSUE_URL, data=encoded_body, headers=HEADERS)

    with urlopen(req) as response:
        json.load(response)


issue_template = '# Unused dependencies \n{}'
table_header = '| Crate | Package | Type |\n|----:|-------:|-------:|'
table_row = '|{}|{}|{}|'

table = [table_header]

nightly_version = get_nightly_from_file()
command = ['cargo', '+{}'.format(nightly_version), 'udeps', '--output', 'json']

current_dir = os.path.dirname(os.path.abspath(__file__))
cwd = os.environ['GITHUB_WORKSPACE']

p = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=cwd)
output = p.stdout.read()
retcode = p.wait()

unused_deps = None

try:
    unused_deps = json.loads(output)
except Exception as e:
    print(output)
    print(e)
    exit(0)

if unused_deps['success']:
    print("No unused dependencies found.")
    exit(0)

for crate in unused_deps['unused_deps'].keys():
    info = unused_deps['unused_deps'][crate]
    create_name = crate.split(" (")[0]
    for normal in info['normal']:
        new_table_row = table_row.format(create_name, normal, 'normal')
        table.append(new_table_row)
    for development in info['development']:
        new_table_row = table_row.format(
            create_name, development, 'development')
        table.append(new_table_row)
    for build in info['build']:
        new_table_row = table_row.format(create_name, build, 'build')
        table.append(new_table_row)

table_rendered = '\n'.join(table)
issue_body = issue_template.format(table_rendered)

if not GH_TOKEN:
    print("Executed locally.")
    exit(0)

issue_status = check_issue_status(issue_body)

if issue_status == 0:
    print("Create new issue.")
    create_issue(issue_body)
elif issue_status == 2:
    print("Issue already created.")
else:
    print("Issue updated.")
    modify_issue(issue_status, issue_body)
