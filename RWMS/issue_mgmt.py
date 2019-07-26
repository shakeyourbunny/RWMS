# GitHub Issue creator
#
# adapted for use in RWMS and touched it up for Python 3
# see https://gist.github.com/JeffPaine/3145490#gistcomment-2558013
import json
import time

import requests

import RWMS.configuration


def get_github_user():
    return RWMS.configuration.load_value("github", "github_username")


def get_github_token():
    return RWMS.configuration.load_value("github", "github_password")


def is_github_configured():
    return (get_github_user() and get_github_token())


def create_issue(title, body):
    USERNAME = get_github_user()
    TOKEN = get_github_token()

    if USERNAME == "" or TOKEN == "":
        return False

    REPO_OWNER = "shakeyourbunny"
    REPO_NAME = "RWMSDB"

    url = 'https://api.github.com/repos/{}/{}/issues'.format(REPO_OWNER, REPO_NAME)

    session = requests.Session()
    session.auth = (USERNAME, TOKEN)

    # Create our issue
    data = {
        'title': title,
        'body': body
    }
    r = session.post(url, json.dumps(data))

    ok = False
    if r.status_code == 201:
        print("Successfully created issue {}.".format(title))
        print("")
        # print(r.content)
        print("Your issue URL is: {}".format(json.loads(r.content)["url"]))
        print("")
        time.sleep(2)
        ok = True
    else:
        print("Could not create issue {0:s}".format(title))
        print("Status Code: {}".format(r.status_code))
        print("Response:\n{}\n".format(r.content))
        print("")
        print("Please contact the author with the full message from above. Thank you.")
        time.sleep(2)
        ok = False
    session.close()

    return ok


# debug
if __name__ == '__main__':

    if is_github_configured():
        print("Github User: {}".format(get_github_user()))
        print("Github Token: {}".format(get_github_token()))
    else:
        print("Github configuration incomplete (user and/or token).")

    pass
