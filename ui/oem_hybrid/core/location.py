# core/location.py — Suprajit Hybrid Cluster
# Background thread location fetch via ip-api.com (no key required).
# Usage: _Loc.fetch()  →  _Loc.text()

import json
import threading
import urllib.request


class _Loc:
    city   = "--"
    region = "--"

    @classmethod
    def fetch(cls):
        """Spawn a daemon thread to fetch city/region from ip-api.com."""
        def _worker():
            try:
                url = "http://ip-api.com/json/?fields=city,regionName"
                with urllib.request.urlopen(url, timeout=4) as resp:
                    data = json.loads(resp.read())
                cls.city   = data.get("city",       "--")
                cls.region = data.get("regionName", "--")
            except Exception:
                pass  # silently keep previous values
        threading.Thread(target=_worker, daemon=True).start()

    @classmethod
    def text(cls) -> str:
        """Return 'City, Region', truncated to 24 chars."""
        s = f"{cls.city}, {cls.region}"
        return s[:24] if len(s) > 24 else s


# Kick off initial fetch at import time
_Loc.fetch()
