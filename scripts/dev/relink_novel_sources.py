"""Re-link novel_sources.source_path to files under /home/user/migrate/novels/.

Run:
    .venv/bin/python scripts/dev/relink_novel_sources.py            # dry-run
    .venv/bin/python scripts/dev/relink_novel_sources.py --apply    # write DB
    .venv/bin/python scripts/dev/relink_novel_sources.py --root /custom/dir

Matching is SHA256 only — title is too noisy (re-uploads share titles but
differ in content). Files whose hash does not appear in DB are skipped
(unmatched-on-disk). DB rows whose hash matches no on-disk file are also
skipped (unmatched-in-DB) and reported.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
from pathlib import Path

import psycopg


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default="/home/user/migrate/novels", help="dir holding original novel txt files")
    parser.add_argument("--apply", action="store_true", help="write changes to DB (default: dry-run)")
    parser.add_argument("--dsn", default=os.environ.get("DATABASE_URL", "host=127.0.0.1 port=5432 dbname=novel_analyzer user=d2 password=d2pass"))
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"ERROR: --root not a directory: {root}", file=sys.stderr)
        return 2

    on_disk: dict[str, Path] = {}
    for path in sorted(root.glob("*.txt")):
        digest = sha256_file(path)
        on_disk.setdefault(digest, path)

    print(f"Indexed {len(on_disk)} unique file hashes under {root}")

    with psycopg.connect(args.dsn, autocommit=False) as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, title, source_hash, source_path
            FROM novel_sources
            WHERE deleted_at IS NULL
            ORDER BY title, id
            """
        )
        rows = cur.fetchall()

        matched: list[tuple[str, str, str, str, str]] = []
        already_ok: list[tuple[str, str, str]] = []
        unmatched: list[tuple[str, str, str, str]] = []

        for row_id, title, source_hash, source_path in rows:
            target = on_disk.get(source_hash)
            current = Path(source_path) if source_path else None
            if current and current.is_file():
                already_ok.append((row_id, title, str(current)))
                continue
            if target is None:
                unmatched.append((row_id, title, source_hash[:12] + "…", source_path or ""))
                continue
            new_path = str(target)
            matched.append((row_id, title, source_hash[:12] + "…", source_path or "", new_path))

        print(f"\n== Already OK: {len(already_ok)} rows ==")
        for r in already_ok[:5]:
            print(f"  {r[0][:8]}… {r[1]:<30s} {r[2]}")
        if len(already_ok) > 5:
            print(f"  ... and {len(already_ok) - 5} more")

        print(f"\n== Will relink: {len(matched)} rows ==")
        for r in matched:
            print(f"  {r[0][:8]}… {r[1]:<30s} hash={r[2]}")
            print(f"    OLD: {r[3]}")
            print(f"    NEW: {r[4]}")

        print(f"\n== Unmatched (no file on disk for this hash): {len(unmatched)} rows ==")
        for r in unmatched:
            print(f"  {r[0][:8]}… {r[1]:<30s} hash={r[2]}  was={r[3]}")

        if not matched:
            print("\nNothing to do.")
            return 0

        if not args.apply:
            print("\nDRY-RUN. Re-run with --apply to write.")
            return 0

        for row_id, _, _, _, new_path in matched:
            cur.execute(
                "UPDATE novel_sources SET source_path = %s, updated_at = now() WHERE id = %s",
                (new_path, row_id),
            )
        conn.commit()
        print(f"\nApplied {len(matched)} updates.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
