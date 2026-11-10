"""Run supporting tests with an existing Hermes-managed environment, never live secrets."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hermes-source", type=Path, required=True, help="Existing official source checkout")
    parser.add_argument("--runtime-home", type=Path, required=True, help="Existing PM metadata home (secret files are not read)")
    parser.add_argument("--runtime-dir", type=Path, help="Existing HERMES_RUNTIME_DIR if used")
    parser.add_argument("--evidence-dir", type=Path, required=True, help="New directory inside this repository")
    args = parser.parse_args()
    source = args.hermes_source.expanduser().resolve()
    output = (ROOT / args.evidence_dir).resolve()
    if not (source / "pm/environments.py").is_file():
        parser.error("Use an existing official Hermes source checkout; this runner installs nothing")
    if not output.is_relative_to(ROOT):
        parser.error("Evidence must stay inside this repository")
    output.mkdir(parents=True, exist_ok=False)
    keep = {"PATH", "HOME", "LANG", "LC_ALL", "LC_CTYPE", "USER", "LOGNAME", "SHELL", "TMPDIR"}
    bootstrap = {key: value for key, value in os.environ.items() if key in keep}
    bootstrap["HERMES_HOME"] = str(args.runtime_home.expanduser().resolve())
    if args.runtime_dir:
        bootstrap["HERMES_RUNTIME_DIR"] = str(args.runtime_dir.expanduser().resolve())
    selection = subprocess.run([sys.executable, "-m", "pm.environments", "--format", "json"],
                               cwd=source, env=bootstrap, capture_output=True, text=True, check=True)
    env = json.loads(selection.stdout)  # Metadata only. Never print the composed environment.
    interpreter = shutil.which("python3", path=env["PATH"])
    if not interpreter:
        raise SystemExit("Existing managed interpreter unavailable; configure Hermes before testing")
    env.update(PYTHONPATH=os.pathsep.join([str(ROOT), env["PYTHONPATH"]]),
               PYTHONDONTWRITEBYTECODE="1", PYTHONNOUSERSITE="1")
    with tempfile.TemporaryDirectory(prefix="blindcouncil-tests-") as test_root:
        env.update(HERMES_HOME=test_root, BLINDCOUNCIL_TEST_ROOT=test_root)
        command = [interpreter, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"]
        result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, timeout=120)
        (output / "stdout.log").write_text(result.stdout)
        (output / "stderr.log").write_text(result.stderr)
        count = re.search(r"Ran (\d+) tests", result.stderr)
        report = {"observed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  "command": command, "exit_code": result.returncode,
                  "test_count": int(count.group(1)) if count else None,
                  "classification": "Supporting tests: actual Hermes SQLite; synthetic identities and transport",
                  "real_telegram_calls": False, "live_secret_configuration_loaded": False,
                  "source_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                                    for path in [ROOT / "__init__.py", ROOT / "plugin.yaml", Path(__file__),
                                                 *sorted((ROOT / "blindcouncil").glob("*.py")),
                                                 *sorted((ROOT / "tests").glob("test_*.py"))]}}
    report["temporary_test_home_removed"] = not Path(test_root).exists()
    (output / "result.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    print(result.stderr, file=sys.stderr)
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
