import sys
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
            % (remaining, total, int((reset_time - time.time()) / 60), reset_time_human)
        )

        while time.time() <= (reset_time + EXTRA_WAIT):
            time.sleep(60)
            print(".", end="")

        print("\n")


def mirror(token, src_org, dst_org):
    g = Github(token, per_page=100)

    src_org = g.get_organization(src_org)
    dst_org = g.get_organization(dst_org)

    print("Building downstream repo index...")
    dst_repos = {r.name: r for r in dst_org.get_repos("public")}

    for src_repo in src_org.get_repos("public"):
        check_rate_limiting(src_repo)

        dst_repo = dst_repos.get(src_repo.name)

        def repo_msg(msg):
            print(f"{src_repo.name}: {msg}")

        if not dst_repo:
            repo_msg("forking...")
            try:
                response = dst_org.create_fork(src_repo)
            except GithubException as e:
                if "contains no Git content" in e._GithubException__data["message"]:
                    # Hit an empty repo, which cannot be forked
                    repo_msg("skipping empty repository")
                    continue
                else:
                    raise e

        else:
            repo_msg("syncing...")

            dst_refs = {r.ref: r for r in dst_repo.get_git_refs()}
            def copy_ref(src_ref, ref_type):
                check_rate_limiting(src_ref)

                encoded_name = urllib.parse.quote(src_ref.name)
                ref_name = "refs/%s/%s" % (ref_type, encoded_name)

                def ref_msg(msg):
                    print(f"{src_repo.name}({ref_name}): {msg}")

                dst_ref = dst_refs.get(ref_name)

                try:
                    if dst_ref and dst_ref.object:
                        if src_ref.commit.sha != dst_ref.object.sha:
                            dst_ref.edit(sha=src_ref.commit.sha, force=True)
                            ref_msg("updated reference")
                    else:
                        dst_repo.create_git_ref(
                            ref=ref_name, sha=src_ref.commit.sha
                        )
                        ref_msg("new reference")

                except GithubException as e:
                    if e.status == 422:
                        ref_msg(f"Github API hit a transient validation error, ignoring for now: {e}")
                    else:
                        raise e

            for src_branch in src_repo.get_branches():
                copy_ref(src_branch, "heads")

            for src_tag in src_repo.get_tags():
                copy_ref(src_tag, "tags")


if __name__ == "__main__":
    p = {}
    for param in ("GITHUB_TOKEN", "SRC_ORG", "DST_ORG"):
        p[param] = os.getenv(param)
        if not p[param]:
            print("No %s supplied in env" % param)
            sys.exit(1)

    mirror(p["GITHUB_TOKEN"], p["SRC_ORG"], p["DST_ORG"])
