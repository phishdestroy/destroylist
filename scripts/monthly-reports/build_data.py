#!/usr/bin/env python3
"""Build the data files of the monthly reports page from rootlist/YYYY/MM.

Runs in the Pages workflow right before the site is built, so the page
always shows every monthly report in the repository, including the current
month. Output (not committed):

  scripts/monthly-reports/data/index.json              years available
  scripts/monthly-reports/data/YYYY.json               one entry per month
  scripts/monthly-reports/data/YYYY-MM-indicators.json  records of a month
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "data"
REPO = os.getenv("PD_REPORTS_REPO_URL", "https://github.com/phishdestroy/destroylist")
RAW = os.getenv("PD_REPORTS_RAW_URL", "https://raw.githubusercontent.com/phishdestroy/destroylist")
BLOB = os.getenv("PD_REPORTS_BLOB_PATH", "/blob/")
INDICATOR_FIELDS = ("domain", "status", "registrar", "tld", "target_brand", "vt_detections", "detected_at")


def load_json(path: Path):
    """Some early reports carry trailing commas; accept them."""
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except ValueError:
        return json.loads(re.sub(r",(\s*[}\]])", r"\1", text))


def revision() -> str:
    for name in ("GITHUB_SHA", "CI_COMMIT_SHA"):
        if os.getenv(name):
            return os.environ[name]
    try:
        return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "main"


def write(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    commit = revision()
    now = datetime.now(timezone.utc).isoformat()
    years = []
    for year_dir in sorted(p for p in (ROOT / "rootlist").iterdir() if re.fullmatch(r"\d{4}", p.name)):
        months = []
        for month_dir in sorted(p for p in year_dir.iterdir() if re.fullmatch(r"\d{2}", p.name)):
            month = f"{year_dir.name}-{month_dir.name}"
            source = month_dir / f"{month}-threats.json"
            if not source.exists():
                continue
            report = load_json(source)
            threats = report.get("threats") or []
            indicators = [{k: t.get(k) for k in INDICATOR_FIELDS} for t in threats if isinstance(t, dict)]
            write(OUT / f"{month}-indicators.json", indicators)
            rel = f"rootlist/{year_dir.name}/{month_dir.name}/{month}-threats.json"
            months.append({
                "meta": report["meta"],
                "stats": report["stats"],
                "top": report.get("top", {}),
                "daily": report.get("daily", {}),
                "source": f"{REPO}{BLOB}{commit}/{rel}",
                "download": f"{RAW}/{commit}/{rel}",
                "indicator_count": len(indicators),
            })
        if months:
            write(OUT / f"{year_dir.name}.json",
                  {"year": int(year_dir.name), "commit": commit, "retrieved_at": now, "months": months})
            years.append({"year": int(year_dir.name), "months": len(months),
                          "total": sum(m["meta"]["total"] for m in months)})
    write(OUT / "index.json", {"commit": commit, "generated_at": now, "years": years})
    summary = ", ".join("%d (%d months)" % (y["year"], y["months"]) for y in years)
    print("monthly-reports data: " + summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
