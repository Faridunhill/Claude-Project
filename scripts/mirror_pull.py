#!/usr/bin/env python3
"""AUTOMATIC MIRROR. Pulls the cloud branch down to Farid's PC.

Runs by itself on a timer. No dependency. Python 3 only.

SAFETY: it never pulls over uncommitted work. If the folder has unsaved changes,
it stops and writes the reason to mirror.log. It fails LOUD, never silent.
(Rule from 2026-09-11: a script that cannot do its job must say so.)

Install on the PC:
    python scripts\\mirror_pull.py --install-task
That creates a Windows scheduled task. It runs every 10 minutes.
To check it worked, open mirror.log in the repo folder.
"""
import argparse
import datetime
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRANCH = "claude/builder-project-restart-so9z19"
LOG = os.path.join(REPO, "mirror.log")


def say(line):
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    text = "%s  %s" % (stamp, line)
    print(text)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(text + "\n")
    except Exception:
        pass


def git(*args):
    r = subprocess.run(["git"] + list(args), cwd=REPO,
                       capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def pull():
    code, out = git("rev-parse", "--is-inside-work-tree")
    if code != 0:
        say("STOPPED. This folder is not a git repository. %s" % out)
        return 1

    code, dirty = git("status", "--porcelain")
    if dirty.strip():
        say("STOPPED. You have unsaved changes. Nothing was pulled.")
        say("   Files: %s" % dirty.replace("\n", " | ")[:300])
        say("   Save or undo them, then it pulls on the next run.")
        return 2

    code, out = git("fetch", "origin", BRANCH)
    if code != 0:
        say("STOPPED. Could not reach GitHub. %s" % out[:300])
        return 3

    code, before = git("rev-parse", "HEAD")
    code, out = git("merge", "--ff-only", "origin/" + BRANCH)
    if code != 0:
        say("STOPPED. The branches have split. %s" % out[:300])
        say("   A person must join them by hand. Nothing was changed.")
        return 4

    code, after = git("rev-parse", "HEAD")
    if before == after:
        say("OK. Nothing new.")
    else:
        code, names = git("diff", "--name-only", before, after)
        n = len([x for x in names.splitlines() if x.strip()])
        say("OK. Pulled. %d files changed." % n)
        for name in names.splitlines()[:20]:
            say("   %s" % name)
    return 0


def install_task():
    cmd = ('schtasks /Create /F /SC MINUTE /MO 10 /TN "FaridunhillMirror" '
           '/TR "\\"%s\\" \\"%s\\"" ' % (sys.executable, os.path.abspath(__file__)))
    say("Creating the timer. Command: %s" % cmd)
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    say((r.stdout + r.stderr).strip()[:400])
    if r.returncode == 0:
        say("DONE. It runs every 10 minutes. Check mirror.log.")
    else:
        say("FAILED. Run this window as Administrator and try again.")
    return r.returncode


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--install-task", action="store_true")
    a = ap.parse_args()
    sys.exit(install_task() if a.install_task else pull())
