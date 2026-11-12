#!/usr/bin/env python3
import subprocess
from pathlib import Path

ROOT = Path("/opt/core-automation")

def main():
    text = (
        "Buongiorno Gelindo!\n"
        "Briefing mattutino Wingman:\n"
        "- Gmail: segnalazione fallimento script Google Apps HUB_ARCHIVIO_2026.\n"
        "- Politica: caso Anac e tensioni partiti.\n"
        "- Calendar: impegni di oggi programmati.\n"
        "- Progetti: Workspace e Actual Budget operativi, monitoraggio ordini in corso."
    )
    
    script = ROOT / "bin" / "ntfy-send.sh"
    cmd = [str(script), "--title", "Wingman — briefing 09:00"]
    proc = subprocess.run(cmd, input=text.encode("utf-8"), capture_output=True)
    if proc.returncode != 0:
        print(f"Error sending ntfy: {proc.stderr.decode('utf-8')}")
    else:
        print("Morning briefing sent successfully.")

if __name__ == "__main__":
    main()
