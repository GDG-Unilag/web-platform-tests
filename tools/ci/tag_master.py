import json
import logging
import os
import sys
import urllib2

here = os.path.abspath(os.path.dirname(__file__))
wpt_root = os.path.abspath(os.path.join(here, os.pardir, os.pardir))

if not(wpt_root) in sys.path:
    sys.path.append(wpt_root)

from tools.wpt.testfiles import get_git_cmd

logging.basicConfig()
logger = logging.getLogger(__name__)


def get_pr(repo, owner, rev):
    url = ("https://api.github.com/search/issues?q=type:pr+is:merged+repo:%s/%s+%s" %
           (repo, owner, rev))
    try:
        resp = urllib2.urlopen(url)
    except Exception as e:
        logger.error(e)
        return None

    if resp.code != 200:
        logger.error("Got HTTP status %s" % resp.code)
        return None

    try:
        data = json.loads(resp.read())
    except ValueError:
        logger.error("Failed to read response as JSON")
        return None

    items = data["items"]
    if len(items) == 0:
        logger.error("No PR found for master")
        return None
    if len(items) > 1:
        logger.warning("Found multiple PRs for master")

    pr = items[0]

    return pr["number"]


def tag(repo, owner, sha, tag):
    data = json.dumps({"refs": "refs/tags/%s" % tag,
                       "sha": sha})
    try:
        resp = urllib2.urlopen("https://%s@api.github.com/repos/%s/%s/git/refs" %
                               (os.environ["GH_TOKEN"],repo, owner),
                               data=data)
    except Exception as e:
        logger.error("Tag creation failed:\n%s" % e)
        return

    if resp.code != 201:
        logger.error("Got HTTP status %s" % resp.code)
    else:
        logger.info("Tagged master as %s" % tag)


def main():
    owner, repo = os.environ["TRAVIS_REPO_SLUG"].split("/", 1)
    if os.environ["TRAVIS_PULL_REQUEST"] != "false":
        logger.info("Not tagging for PR")
        return
    if os.environ["TRAVIS_BRANCH"] != "master":
        logger.info("Not tagging for non-master branch")
        return

    git = get_git_cmd(wpt_root)
    head_rev = git("rev-parse", "HEAD")

    pr = get_pr(owner, repo, head_rev)
    if pr is not None:
        tag(owner, repo, head_rev, "merge_pr_%s" % pr)


if __name__ == "__main__":
    main()
