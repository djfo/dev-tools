import re
import subprocess
import sys

def error(str: str):
    sys.stderr.write("%s\n" % str)

def get_merge_commits(base: str) -> list[str]:
    completed = subprocess.run(
        [
            "git",
            "log",
            "--pretty=tformat:%h,%p", "%s..HEAD" % base
        ],
        capture_output=True,
        encoding='utf-8'
    )
    re_merge_commit = r'^([0-9a-fA-f]+),([0-9a-fA-F]+) ([0-9a-fA-F]+)$'
    output = completed.stdout
    lines = output.splitlines()
    merge_commits = []
    for line in lines:
        match = re.match(re_merge_commit, line)
        if match:
            merge_commits.append(match.group(1))
    return merge_commits

def find_matches(merge_commits, re_extract) -> list[str]:
    matches = []
    for commit_hash in merge_commits:
        completed = subprocess.run(
            [
                "git",
                "show",
                "--pretty=tformat:%s",
                commit_hash
            ],
            capture_output=True,
            encoding="utf-8"
        )
        first_line = completed.stdout.splitlines()[0]
        match = re.search(re_extract, first_line, )
        if match:
            matches.append(match.group(1))
        else:
            error("no match: »%s«" % first_line)
    return matches

def main():
    commit_hash, pattern, *rest = sys.argv[1:]
    merge_commits = get_merge_commits(commit_hash)
    print("Number of merge commits: %d" % len(merge_commits))
    print()

    print("Merge commits:")
    if not merge_commits:
        print("(none)")
    for commit in merge_commits:
        print("- %s" % commit)
    print()

    print("Matches:")
    matches = find_matches(merge_commits, pattern)
    if not matches:
        print("(none)")
    for title in matches:
        print("- %s" % title)

if __name__ == "__main__":
    main()
