"""PowerShell care for the PC, with the dangerous half behind a gate.

Design rule: **the model never writes PowerShell.** It picks a name from the registry
below and we run the fixed string. That single decision is what keeps a model-driven
manager off the list of things that can brick a machine — there is no prompt that makes
`winget list` into `rm -rf`, because the model's only input is a key lookup.

Two tiers:
  CHECK   read-only. Runs unattended, no approval.
  ACTION  changes the machine. Requires an approval token Farid issued for that exact
          name. Tokens are single-use and expire.

Anything destructive — format, registry writes, driver deletion, anything under the ARK —
is simply absent. Not gated: absent. Adding one is a deliberate edit to this file.
"""

from __future__ import annotations

import json
import platform
import shutil
import subprocess
from dataclasses import dataclass
from typing import Any, Literal

Tier = Literal["check", "action"]


@dataclass(frozen=True)
class Command:
    name: str
    tier: Tier
    summary: str
    script: str
    # Timeout in seconds. Updates are slow; checks should be quick.
    timeout: int = 120


def _ps(body: str) -> str:
    """Wrap a pipeline so it returns JSON we can hand back to the model as data."""
    return f"{body} | ConvertTo-Json -Depth 4 -Compress"


# --------------------------------------------------------------------------------------
# CHECKS — read-only. Safe to run on a schedule with nobody watching.
# --------------------------------------------------------------------------------------

_CHECKS: tuple[Command, ...] = (
    Command(
        "updates.available", "check",
        "Packages with a newer version available (winget, list only).",
        "winget upgrade --include-unknown --accept-source-agreements",
        timeout=180,
    ),
    Command(
        "updates.installed", "check",
        "The last 15 Windows hotfixes and when they landed.",
        _ps("Get-HotFix | Sort-Object InstalledOn -Descending | "
            "Select-Object -First 15 HotFixID,Description,InstalledOn"),
    ),
    Command(
        "drivers.problem", "check",
        "Devices Windows reports as not working (Code 28, errors, unknown).",
        _ps("Get-PnpDevice | Where-Object { $_.Status -ne 'OK' } | "
            "Select-Object Status,Class,FriendlyName,InstanceId"),
    ),
    Command(
        "gpu.status", "check",
        "GPU name, driver version and driver date — the transcription bottleneck.",
        _ps("Get-CimInstance Win32_VideoController | "
            "Select-Object Name,DriverVersion,DriverDate,AdapterRAM"),
    ),
    Command(
        "disk.free", "check",
        "Free and total space per volume, in GB. The ARK is ~2.3 GB and growing.",
        _ps("Get-Volume | Where-Object DriveLetter | Select-Object DriveLetter,"
            "FileSystemLabel,@{n='FreeGB';e={[math]::Round($_.SizeRemaining/1GB,1)}},"
            "@{n='SizeGB';e={[math]::Round($_.Size/1GB,1)}}"),
    ),
    Command(
        "restart.pending", "check",
        "Whether Windows is holding a restart (updates half-applied).",
        _ps("[pscustomobject]@{ RebootPending = (Test-Path "
            "'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Component Based "
            "Servicing\\RebootPending') }"),
    ),
    Command(
        "temp.size", "check",
        "How much is sitting in the user temp folder, in MB.",
        _ps("[pscustomobject]@{ TempMB = [math]::Round(((Get-ChildItem $env:TEMP -Recurse "
            "-File -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum/1MB),1) }"),
    ),
    Command(
        "defender.status", "check",
        "Antivirus on/off and how old the signatures are.",
        _ps("Get-MpComputerStatus | Select-Object AntivirusEnabled,"
            "RealTimeProtectionEnabled,AntivirusSignatureLastUpdated"),
    ),
    Command(
        "startup.items", "check",
        "What launches at boot — the usual cause of a slow machine.",
        _ps("Get-CimInstance Win32_StartupCommand | Select-Object Name,Command,Location"),
    ),
    Command(
        "memory.pressure", "check",
        "Free vs total RAM in GB, and the top 5 memory consumers.",
        _ps("[pscustomobject]@{ "
            "FreeGB = [math]::Round((Get-CimInstance Win32_OperatingSystem)."
            "FreePhysicalMemory/1MB,1); "
            "TotalGB = [math]::Round((Get-CimInstance Win32_ComputerSystem)."
            "TotalPhysicalMemory/1GB,1); "
            "Top = (Get-Process | Sort-Object WS -Descending | Select-Object -First 5 "
            "Name,@{n='WorkingSetMB';e={[math]::Round($_.WS/1MB,0)}}) }"),
    ),
)

# --------------------------------------------------------------------------------------
# ACTIONS — change the machine. Approval token required, every single time.
# --------------------------------------------------------------------------------------

_ACTIONS: tuple[Command, ...] = (
    Command(
        "updates.apply", "action",
        "Install all available winget package upgrades.",
        "winget upgrade --all --include-unknown --silent "
        "--accept-source-agreements --accept-package-agreements",
        timeout=3600,
    ),
    Command(
        "temp.clean", "action",
        "Delete files in the user TEMP folder older than 7 days. TEMP only — nothing else.",
        "Get-ChildItem $env:TEMP -Recurse -File -ErrorAction SilentlyContinue | "
        "Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) } | "
        "Remove-Item -Force -ErrorAction SilentlyContinue; "
        "Write-Output 'temp cleaned'",
        timeout=600,
    ),
    Command(
        "defender.quickscan", "action",
        "Run a Defender quick scan.",
        "Start-MpScan -ScanType QuickScan; Write-Output 'scan complete'",
        timeout=1800,
    ),
    Command(
        "restart.now", "action",
        "Restart the computer. Everything unsaved is lost.",
        "Restart-Computer -Force",
        timeout=30,
    ),
)

REGISTRY: dict[str, Command] = {c.name: c for c in (*_CHECKS, *_ACTIONS)}


def catalogue() -> list[dict[str, str]]:
    return [
        {"name": c.name, "tier": c.tier, "summary": c.summary}
        for c in REGISTRY.values()
    ]


class NotApproved(PermissionError):
    """An ACTION was attempted without a valid approval token."""


def powershell_binary() -> str | None:
    """pwsh (7+) if present, else Windows PowerShell, else None."""
    return shutil.which("pwsh") or shutil.which("powershell")


def run(name: str, *, approval: str | None = None, approvals: Any = None) -> dict[str, Any]:
    """Run a registry command by name.

    `approvals` is an ApprovalBook (see approvals.py); ACTION commands consume a token
    from it. CHECK commands ignore both approval arguments entirely.
    """
    cmd = REGISTRY.get(name)
    if cmd is None:
        return {
            "ok": False,
            "error": f"No such command {name!r}. Registry: {sorted(REGISTRY)}",
        }

    if cmd.tier == "action":
        if approvals is None or not approvals.consume(name, approval):
            raise NotApproved(
                f"{name!r} changes the machine and needs an approval token from Farid. "
                f"He issues one with: desk approve {name}"
            )

    shell = powershell_binary()
    if shell is None:
        return {
            "ok": False,
            "unavailable": True,
            "error": (
                "PowerShell not found. This module only does real work on Windows "
                "(or Linux with pwsh installed)."
            ),
            "platform": platform.system(),
            "would_run": cmd.script,
        }

    try:
        proc = subprocess.run(
            [shell, "-NoProfile", "-NonInteractive", "-Command", cmd.script],
            capture_output=True, text=True, timeout=cmd.timeout,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": f"{name} timed out after {cmd.timeout}s"}

    out = proc.stdout.strip()
    parsed: Any = None
    if out.startswith(("{", "[")):
        try:
            parsed = json.loads(out)
        except json.JSONDecodeError:
            parsed = None

    return {
        "ok": proc.returncode == 0,
        "name": name,
        "tier": cmd.tier,
        "exit_code": proc.returncode,
        "data": parsed,
        "stdout": None if parsed is not None else out[:8000],
        "stderr": proc.stderr.strip()[:2000] or None,
    }
