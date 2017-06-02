# -*- coding: utf-8 -*-
import httplib
import os
import sys

import subprocess

# import CRAB3 stuff
from CRABAPI.RawCommand import crabCommand


def retry(nattempts, exception=None):
    """
    Decorator allowing to retry an action several times before giving up.
    @params:
        nattempts  - Required: maximal number of attempts (Int)
        exception  - Optional: if given, only catch this exception, otherwise catch 'em all (Exception)
    """
    
    def tryIt(func):
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < nattempts - 1:
                try:
                    return func(*args, **kwargs)
                except (exception if exception is not None else Exception):
                    attempts += 1
            return func(*args, **kwargs)
        return wrapper
    return tryIt


@retry(5, httplib.HTTPException)
def send_crab_command(*args, **kwargs):
    """
    Send a crab command but try again (max 5 times) if server doesn't answer.
    """
    return crabCommand(*args, **kwargs)


def sum_dicts(a, b):
    """
    Sum each value of the dicts a et b and return a new dict
    """

    if len(a) == 0 and len(b) == 0:
        return {}

    if len(a) == 0:
        for key in b.viewkeys():
            a[key] = 0

    if len(b) == 0:
        for key in a.viewkeys():
            b[key] = 0

    if a.viewkeys() != b.viewkeys():
        print("Warning: files content are different. This is not a good sign, something really strange happened!")
        return None

    r = {}
    for key in a.viewkeys():
        r[key] = a[key] + b[key]

    return r


def print_progress(iteration, total, prefix='', suffix='', decimals=1, bar_length=40):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        bar_length  - Optional  : character length of bar (Int)
    """
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '█' * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),

    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()


def load_request(folder):
    """
    Return request cache from a crab task folder
    """
    
    import pickle

    cache = os.path.join(folder, '.requestcache')
    with open(cache) as f:
        cache = pickle.load(f)
        return cache

def parseGithubUrl(fullUrl, stripDotGit=False):
    """ Get user/organisation and repository name from github remote name (optionally removing the trailing ".git") """
    remote, repo = fullUrl.split(":")[-1].split("/")[-2:]
    if stripDotGit:
        repo = repo.strip(".git")
    return remote, repo
def getRemoteUrl(gitDir, remoteName):
    """ Get the url of the remote with name remoteName for the git repository in gitDir """
    try:
        return subprocess.check_output(["git", "config", "--get", "remote.{0}.url".format(remoteName)], cwd=gitDir).strip()
    except subprocess.CalledProcessError, e:
        raise AssertionError('Repository at "{0}" has no remote with name "{1}".\nCommand "{2}" returned {3:d} with output "{4}"'.format(gitDir, remoteName, " ".join(e.cmd), e.returncode, e.output))

def getGitTagRepoUrl(gitCallPath):
    # get the stuff needed to write a valid url: name on github, name of repo, for both origin and upstream
    originUrl   = getRemoteUrl(gitCallPath, "origin")
    remoteOrigin  , repoOrigin   = parseGithubUrl(originUrl  , stripDotGit=True)
    upstreamUrl = getRemoteUrl(gitCallPath, "upstream")
    remoteUpstream, repoUpstream = parseGithubUrl(upstreamUrl, stripDotGit=True)
    # get the hash of the commit
    # Well, note that actually it should be the tag if a tag exist, the hash is the fallback solution
    gitHash = subprocess.check_output(['git', 'describe', '--tags', '--always', '--dirty'], cwd=gitCallPath).strip()
    if 'dirty' in gitHash:
        raise AssertionError("Aborting: your working tree for repository", repoOrigin, "is dirty, please clean the changes not staged/committed before inserting this in the database") 
    # get the list of branches in which you can find the hash
    branches = [ br.strip() for br in subprocess.check_output(['git', 'branch', '-r', '--contains', gitHash], cwd=gitCallPath).strip().split("\n") ]
    if any("upstream" in br for br in branches):
        url = "https://github.com/{remote}/{repo}/tree/{gitHash}".format(remote=remoteUpstream, repo=repoUpstream, gitHash=gitHash)
        remote = remoteUpstream
        repo = repoUpstream
    elif any("origin" in br for br in branches):
        remote = remoteOrigin
        repo = repoOrigin
    elif any("/" in br for br in branches):
        ## assume the remote name is the user/org on github, and the repository name is the same as origin
        theBranch = next(br for br in branches if "/" in br)
        remote = theBranch.split("/")[0]
        repo = repoOrigin
    else:
        print "PLEASE PUSH YOUR CODE!!! this result CANNOT be reproduced / bookkept outside of your ingrid session, so there is no point into putting it in the database, ABORTING now"
        print "Remote branches that contain the checked-out commit: {0}".format(", ".join(branches))
        raise AssertionError("Code from repository " + repoUpstream + " has not been pushed")
    url = "https://github.com/{remote}/{repo}/tree/{gitHash}".format(remote=remote, repo=repo, gitHash=gitHash)
    return gitHash, repo, url
