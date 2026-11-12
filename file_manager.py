"""Gestione documenti dentro /opt/core-automation/data. Non esce da quella cartella."""
from __future__ import annotations

from pathlib import Path

ROOT = Path("/opt/core-automation")
DATA = (ROOT / "data").resolve()


def _in_data(name: str) -> Path:
    if not name or name.strip() == "":
        raise ValueError("manca il nome del file")
    raw = Path(name)
    if raw.is_absolute():
        raise ValueError("serve un nome relativo a data/")
    target = (DATA / raw).resolve()
    if target != DATA and DATA not in target.parents:
        raise ValueError("percorso fuori da data/")
    return target


def append_text(name: str, text: str) -> Path:
    path = _in_data(name)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(text)
    return path


def read_text(name: str) -> str:
    path = _in_data(name)
    return path.read_text(encoding="utf-8")


def extract_pdf_text(name: str) -> str:
    path = _in_data(name)
    try:
        from pypdf import PdfReader
        from pypdf.errors import PdfReadError
    except ImportError as exc:
        return f"pypdf non disponibile: {exc}"
    try:
        reader = PdfReader(str(path))
        parts = [(page.extract_text() or "") for page in reader.pages]
    except PdfReadError as exc:
        return f"PDF non leggibile: {exc}"
    except Exception as exc:
        return f"Errore di lettura PDF: {type(exc).__name__}: {exc}"
    return "\n".join(parts).strip()
