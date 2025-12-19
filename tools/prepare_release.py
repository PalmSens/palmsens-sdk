from pathlib import Path
import argparse
import subprocess as sp
from contextlib import contextmanager
import os


ROOT = Path(__file__).parents[1]

PR_BODY = """\
This PR prepares for a new release of the {sdk} SDK.

- branch: `release-{tag}`
- version: `{version}`
- sdk: `{sdk}`
"""


@contextmanager
def work_directory(path: Path):
    prev_cwd = Path.cwd().resolve()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(prev_cwd)


def announce(tag: str):
    releases_path = Path(
        ROOT, "docs", "start", "modules", "ROOT", "pages", "releases.adoc"
    )
    assert releases_path.exists()
    lines = releases_path.read_text().splitlines()

    index = lines.index("// latest")

    if tag in lines[index + 1]:
        print("Tag already exists, skipping")
    else:
        new_line = (
            f"- https://github.com/palmsens/palmsens_sdk/releases/tag/maui-{tag}[{tag}]"
        )
        lines.insert(index + 1, new_line)
        releases_path.write_text("\n".join(lines) + "\n", encoding="UTF-8")
        print(f"Tag added to {releases_path.name}")

    sp.check_call(["git", "add", f"{releases_path}"])
    sp.check_call(["git", "commit", "-m", "Updated release index"])


def bump_version(sdk: str, version: str):
    workdir = ROOT / sdk

    with work_directory(workdir):
        sp.check_call(
            ["bump-my-version", "bump", "--new-version", version, "patch", "--commit"]
        )

    print(f"Bumped {sdk} version to {version}")


def prepare_pr(sdk: str, version: str, base_branch="main"):
    sp.check_call(["git", "checkout", f"origin/{base_branch}"])

    release_branch = f"release-{tag}"

    sp.run(
        ["git", "checkout", "-b", release_branch, f"origin/{base_branch}"],
        check=True,
    )

    print(f"Created branch {release_branch}")

    announce(tag)
    bump_version(sdk, version)

    sp.run(
        ["git", "push", "origin", f"HEAD:{release_branch}", "--force"],
        check=True,
    )
    print(f"Pushed {release_branch}")

    body = PR_BODY.format(version=version, sdk=sdk, tag=tag)
    print(body)

    sp.run(
        [
            "gh",
            "pr",
            "create",
            f"--base={base_branch}",
            f"--head={release_branch}",
            f"--title=Release {sdk}-{version}",
            f"--body={body}",
            "--draft",
        ],
        check=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("sdk", type=str)
    parser.add_argument("--version", type=str)
    options = parser.parse_args()

    tag = f"{options.sdk}-{options.version}"
    print(f"{tag=}")

    prepare_pr(
        sdk=options.sdk,
        version=options.version,
    )
