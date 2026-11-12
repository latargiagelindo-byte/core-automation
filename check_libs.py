"""Controlla le librerie del primo passo. Non installa nulla e non scarica nulla."""
from __future__ import annotations

import importlib.util
import sys

# os è nella libreria standard. Gli altri nomi sono i pacchetti pip.
CHECKS = (
    ("os", None),
    ("requests", "requests"),
    ("pypdf", "pypdf"),
    ("playwright", "playwright"),
)


def present(module: str) -> bool:
    return importlib.util.find_spec(module) is not None


def main() -> int:
    missing: list[str] = []
    for module, package in CHECKS:
        ok = present(module)
        stato = "presente" if ok else "assente"
        print(f"{module}: {stato}")
        if not ok and package:
            missing.append(package)
    if not missing:
        print("Le librerie controllate ci sono già.")
        return 0
    print("Comandi, da lanciare a mano dentro questo progetto:")
    print(f"{sys.executable} -m venv /opt/core-automation/.venv")
    joined = " ".join(missing)
    print(f"/opt/core-automation/.venv/bin/python -m pip install {joined}")
    if "playwright" in missing:
        print("/opt/core-automation/.venv/bin/python -m playwright install chromium")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
