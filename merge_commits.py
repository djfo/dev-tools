import re
import subprocess
import sys
from typing import Optional


def run(argv: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        argv,
        capture_output=True,
        encoding='utf-8'
    )


def error(str: str) -> None:
    sys.stderr.write("%s\n" % str)


def get_merge_commits(base: Optional[str], since: Optional[str]) -> list[str]:
    argv = [
        "git",
        "log",
        "--pretty=tformat:%h,%p"
    ]
    if base:
        argv.append("%s..HEAD" % base)
    if since:
        argv.append('--since=%s' % since)
    completed = run(argv)
    re_merge_commit = r'^([0-9a-fA-f]+),([0-9a-fA-F]+) ([0-9a-fA-F]+)$'
    output = completed.stdout
    lines = output.splitlines()
    merge_commits = []
    for line in lines:
        match = re.match(re_merge_commit, line)
        if match:
            merge_commits.append(match.group(1))
    return merge_commits


def find_matches(merge_commits: list[str], patterns: list[str]) -> list[str]:
    matches = []
    for commit_hash in merge_commits:
        completed = run(
            [
                "git",
                "show",
                "--pretty=tformat:%s",
                commit_hash
            ]
        )
        first_line = completed.stdout.splitlines()[0]
        found_match = False
        for pattern in patterns:
            match = re.search(pattern, first_line)
            if match:
                matches.append(match.group(1))
                found_match = True
                continue
        if not found_match:
            error("no match: »%s«" % first_line)
    return matches


def partition_args(raw: list[str]):
    args = []
    flags = []
    for arg in raw:
        if len(arg) > 0 and arg[0] == '-':
            flags.append(arg)
        else:
            args.append(arg)
    return (args, flags)


def main() -> None:
    commit_hash = None
    patterns = []
    if len(sys.argv) > 1:
        commit_hash, *patterns = sys.argv[1:]
    merge_commits = get_merge_commits(commit_hash)
    print("Number of merge commits: %d" % len(merge_commits))
    print()

    print("Merge commits:")
    if not merge_commits:
        print("(none)")
    for commit in merge_commits:
        print("- %s" % commit)
    print()

    if len(patterns) > 0:
        print("Matches:")
        matches = find_matches(merge_commits, patterns)
        if not matches:
            print("(none)")
        for title in matches:
            print("- %s" % title)


if __name__ == "__main__":
    main()
