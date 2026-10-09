#!/usr/bin/env python3
"""Select (or create) an available iPhone simulator and emit SIM_NAME=... .

Used by .github/workflows/component-ci.yml on macOS runners. Writes the
choice to stdout and, when given a path argument, also to that file as
SIM_NAME=<name> (suitable for $GITHUB_OUTPUT via `echo "name=$(...)"`).
"""
import json
import subprocess
import sys
import uuid


def simctl(*args):
    out = subprocess.run(
        ["xcrun", "simctl", "list", "-j", *args],
        capture_output=True, text=True, check=True,
    )
    return json.loads(out.stdout)


def main() -> int:
    data = simctl("devices", "available")
    name = None
    for _runtime, devices in data.get("devices", {}).items():
        for d in devices:
            if d.get("isAvailable") and d.get("name", "").startswith("iPhone"):
                name = d["name"]
                break
        if name:
            break

    if name is None:
        # No pre-created simulator on the image: create one.
        dtypes = simctl("devicetypes")["devicetypes"]
        runtimes = simctl("runtimes")["runtimes"]
        iphone = next((d for d in reversed(dtypes) if d["name"].startswith("iPhone")), None)
        ios_rt = next(
            (r for r in reversed(runtimes)
             if r.get("isAvailable") and r["platform"] == "iOS"),
            None,
        )
        if not iphone or not ios_rt:
            print("::error::No iPhone device type or iOS runtime available", file=sys.stderr)
            return 1
        name = "MrSpicySim-" + uuid.uuid4().hex[:6]
        subprocess.run(
            ["xcrun", "simctl", "create", name, iphone["identifier"], ios_rt["identifier"]],
            check=True,
        )

    print(f"Selected simulator: {name}")
    if len(sys.argv) > 1:
        with open(sys.argv[1], "w") as f:
            f.write(f"SIM_NAME={name}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
