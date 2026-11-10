"""Review changed public files without reading tokens or exporting private participant IDs.

Historical delivery rows include synthetic fixtures. Only identities corroborated
by native receipts belong to the real-identity exclusion set. The native marker
is local observability, not a tamper-proof authenticity claim.
"""
import argparse
from contextlib import closing
import json
from pathlib import Path
import re
import sqlite3
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def native_actor_ids(conn):
    return {str(row[0]) for row in conn.execute("""SELECT DISTINCT r.user_id FROM receipts r
        JOIN receipt_origins o USING(round_id,user_id) WHERE o.origin='hermes-telegram'""")}


def findings(text, identities):
    problems = []
    if any(re.search(r"(?<!\d)" + re.escape(value) + r"(?!\d)", text) for value in identities):
        problems.append("private native participant identifier")
    if re.search(r"https?://api\.telegram\.org/bot\d{5,}:", text):
        problems.append("credential-bearing Telegram URL")
    tokens = re.findall(r"(?<!\d)\d{5,}:[A-Za-z0-9_-]{20,}", text)
    if any(token != "777000:SYNTHETIC_NO_VALID_BOT_TOKEN" for token in tokens):
        problems.append("token-shaped value")
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True, help="New report path inside workspace")
    args = parser.parse_args()
    output = (ROOT / args.report).resolve()
    if not output.is_relative_to(ROOT) or output.exists():
        raise SystemExit("Use a new report path inside the workspace")
    database = ROOT / "isolated-home/plugin-data/blindcouncil/data.db"
    with closing(sqlite3.connect(f"file:{database}?mode=ro", uri=True)) as conn:
        identities = native_actor_ids(conn)
    if len(identities) != 2:
        raise SystemExit("Expected two corroborated native identities; review safely without printing them")
    def git(*arguments):
        return subprocess.run(["git", *arguments], cwd=ROOT, capture_output=True, text=True, check=True).stdout.splitlines()
    names = set(git("diff", "--name-only", "--diff-filter=AM"))
    names.update(git("diff", "--cached", "--name-only", "--diff-filter=AM"))
    names.update(git("ls-files", "--others", "--exclude-standard"))
    issues = []
    for name in sorted(names):
        path = ROOT / name
        if path.is_file():
            issues.extend({"path": name, "issue": issue} for issue in findings(path.read_text(errors="replace"), identities))
    whitespace = subprocess.run(["git", "diff", "--check", "--", "*.py", "*.md", "*.yaml"],
                                cwd=ROOT, capture_output=True, text=True)
    source_match = all((ROOT / "isolated-home/plugins/blindcouncil" / name).is_file() and
                       (ROOT / "blindcouncil" / name).read_bytes() ==
                       (ROOT / "isolated-home/plugins/blindcouncil" / name).read_bytes()
                       for name in [path.name for path in (ROOT / "blindcouncil").glob("*.py")])
    report = {"command": "python3 probes/review_public_changes.py --report " + args.report,
              "changed_files_checked": len(names), "native_identity_count": len(identities),
              "secret_scan_issues": issues, "source_whitespace_exit_code": whitespace.returncode,
              "installed_python_sources_match": source_match,
              "passed": not issues and whitespace.returncode == 0 and source_match,
              "token_files_read": False, "private_identity_values_exported": False}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x") as stream:
        stream.write(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
