import datetime
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


def partition_args(raw: list[str]) -> tuple[list[str], dict[str, Optional[str]]]:
    args = []
    flags = {}
    for arg in raw:
        if len(arg) > 0 and arg[0] == '-':
            key, *value = arg.split('=', 1)
            flags[key] = value[0] if len(value) else None
        else:
            args.append(arg)
    return (args, flags)


def main() -> None:
    (args, flags) = partition_args(sys.argv[1:])

    commit_hash = None
    patterns = []
    since = None
    if '--today' in flags:
        today = datetime.date.today()
        since = '%s 00:00:00' % today.isoformat()
        patterns = args
    elif len(args):
        commit_hash, *patterns = args
    merge_commits = get_merge_commits(commit_hash, since)
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
