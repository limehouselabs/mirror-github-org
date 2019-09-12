import os
import time
import datetime
import urllib.parse

from github import Github
from github.GithubException import UnknownObjectException, GithubException

RATE_BUFFER = 100
EXTRA_WAIT = 60


def check_rate_limiting(rl):
    remaining, total = rl._requester.rate_limiting

    if remaining < RATE_BUFFER:
        reset_time = rl._requester.rate_limiting_resettime
        reset_time_human = datetime.datetime.fromtimestamp(
            int(reset_time)
        ) + datetime.timedelta(seconds=EXTRA_WAIT)

        print(
            "\nWAITING: Remaining rate limit is %s of %s. Waiting %s mins for reset at %s before continuing.\n"
            % (remaining, total, int((reset_time - time.time())/60), reset_time_human)
        )

        while time.time() <= (reset_time + EXTRA_WAIT):
            time.sleep(60)
            print(".", end="")

        print("\n")


def mirror(token, src_org, dst_org):
    g = Github(token)

    src_org = g.get_organization(src_org)
    dst_org = g.get_organization(dst_org)

    for src_repo in src_org.get_repos("public", sort="pushed", direction="desc"):
        check_rate_limiting(src_repo)

        dst_repo = None
        try:
            dst_repo = dst_org.get_repo(src_repo.name)
        except UnknownObjectException:
            pass

        if not dst_repo:
            print("\n\nForking %s..." % src_repo.name, end="")
            try:
                response = dst_org.create_fork(src_repo)
            except GithubException as e:
                if "contains no Git content" in e._GithubException__data["message"]:
                    # Hit an empty repo, which cannot be forked
                    print("\n * Skipping empty repository", end="")
                    continue
                else:
                    raise e

        else:
            print("\n\nSyncing %s..." % src_repo.name, end="")

            updated = False
            for src_branch in src_repo.get_branches():
                check_rate_limiting(src_branch)

                print("\n - %s " % src_branch.name, end=""),
                encoded_name = urllib.parse.quote(src_branch.name)

                try:
                    dst_ref = dst_repo.get_git_ref(ref="heads/%s" % encoded_name)
                except UnknownObjectException:
                    dst_ref = None

                if dst_ref:
                    if src_branch.commit.sha != dst_ref.object.sha:
                        print("(updated)", end="")
                        dst_ref.edit(sha=src_branch.commit.sha, force=True)
                        updated = True
                else:
                    print("(new)", end="")
                    dst_repo.create_git_ref(
                        ref="refs/heads/%s" % encoded_name, sha=src_branch.commit.sha
                    )
                    updated = True

            if not updated:
                print("\n\nNo more updates to mirror. Ending run.")
                sys.exit(0)


if __name__ == "__main__":
    p = {}
    for param in ("GITHUB_TOKEN", "SRC_ORG", "DST_ORG"):
        p[param] = os.getenv(param)
        if not p[param]:
            print("No %s supplied in env" % param)
            sys.exit(1)

    mirror(p["GITHUB_TOKEN"], p["SRC_ORG"], p["DST_ORG"])
