"""Print the repo files deployed to the Claude Project and their Project paths (docs/deploy.md).

  python3 scripts/deploy_manifest.py          # "repo_path<TAB>project_path" lines
"""

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INCLUDE_TOP = ["README.md", "VERSION", "CHANGELOG.md"]
INCLUDE_DIRS = ["framework", "integrations", "tasks", "onboarding", "docs", "scripts"]
EXCLUDE_PARTS = {"tests", "__pycache__", ".pytest_cache"}


def manifest():
    files = [f for f in INCLUDE_TOP if os.path.exists(os.path.join(ROOT, f))]
    for d in INCLUDE_DIRS:
        for base, dirs, names in os.walk(os.path.join(ROOT, d)):
            dirs[:] = sorted(x for x in dirs if x not in EXCLUDE_PARTS)
            for n in sorted(names):
                if n.endswith((".md", ".py")):
                    files.append(os.path.relpath(os.path.join(base, n), ROOT))
    return [(f, "agent/" + f.replace(os.sep, "/")) for f in files]


if __name__ == "__main__":
    for repo_path, project_path in manifest():
        print(f"{repo_path}\t{project_path}")
