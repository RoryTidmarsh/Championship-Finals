"""
Error logging module for Championship Finals.

Writes structured JSON entries to the console and persists each error in a
local SQLite database (error_log.db) so they can be reviewed later via the
/api/error-log endpoint.

For webscraping errors, the raw HTML of the page being processed at the time
of the failure is stored in the database for post-mortem inspection.
"""
import json
import logging
import sqlite3
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_DB_PATH = Path(__file__).parent.parent.parent / "error_log.db"

# ---------------------------------------------------------------------------
# Standard Python JSON logger (console output)
# ---------------------------------------------------------------------------
_logger = logging.getLogger("championship_finals")
if not _logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(message)s"))
    _logger.addHandler(_handler)
_logger.setLevel(logging.DEBUG)


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS error_log (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp    TEXT    NOT NULL,
            request_id   TEXT,
            error_type   TEXT    NOT NULL,
            source       TEXT    NOT NULL,
            cause        TEXT    NOT NULL,
            context      TEXT,
            html_snapshot TEXT
        )
        """
    )
    conn.commit()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def log_error(
    *,
    error_type: str,
    source: str,
    cause: str,
    request_id: str | None = None,
    context: dict | None = None,
    html_snapshot: str | None = None,
    exc: BaseException | None = None,
) -> str:
    """
    Record an error to the console (JSON) and to the SQLite database.

    Args:
        error_type:    Short category label, e.g. "ScrapingError", "ColumnMismatch",
                       "MergeError", "NetworkError".
        source:        The function / module where the error originated.
        cause:         Human-readable explanation of *why* the error occurred.
        request_id:    Optional ID that ties several log entries to one HTTP request.
        context:       Any extra key/value pairs useful for diagnosis (URLs, IDs, …).
        html_snapshot: Raw HTML of the page being scraped at the time of the error.
                       Should only be supplied for scraping-related errors.
        exc:           The live exception object; its traceback is included in the log.

    Returns:
        A newly generated error_id string that can be surfaced to the caller.
    """
    error_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()

    tb_text = traceback.format_exc() if exc is not None else None

    # --- Console (JSON) log ---
    log_payload: dict = {
        "level": "ERROR",
        "timestamp": timestamp,
        "error_id": error_id,
        "request_id": request_id,
        "error_type": error_type,
        "source": source,
        "cause": cause,
        "context": context or {},
    }
    if tb_text and tb_text.strip() != "NoneType: None":
        log_payload["traceback"] = tb_text

    _logger.error(json.dumps(log_payload, default=str))

    # --- Persist to SQLite ---
    try:
        with _get_conn() as conn:
            _ensure_table(conn)
            conn.execute(
                """
                INSERT INTO error_log
                    (timestamp, request_id, error_type, source, cause, context, html_snapshot)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    timestamp,
                    request_id,
                    error_type,
                    source,
                    cause,
                    json.dumps(context or {}, default=str),
                    html_snapshot,
                ),
            )
    except Exception as db_exc:  # pragma: no cover – DB write failure must not mask original
        _logger.error(
            json.dumps({"level": "ERROR", "source": "error_logger", "cause": f"DB write failed: {db_exc}"})
        )

    return error_id


def log_info(*, source: str, message: str, request_id: str | None = None, context: dict | None = None) -> None:
    """Emit a structured INFO entry to the console (not persisted to DB)."""
    payload = {
        "level": "INFO",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_id": request_id,
        "source": source,
        "message": message,
        "context": context or {},
    }
    _logger.info(json.dumps(payload, default=str))


def get_recent_errors(limit: int = 20) -> list[dict]:
    """
    Return the most recent errors from the database, newest first.

    Args:
        limit: Maximum number of records to return (default 20).

    Returns:
        List of dicts with keys: id, timestamp, request_id, error_type,
        source, cause, context, has_html_snapshot.
        The html_snapshot content itself is *not* returned here to keep
        response payloads small; use get_error_detail() for that.
    """
    try:
        with _get_conn() as conn:
            _ensure_table(conn)
            rows = conn.execute(
                """
                SELECT id, timestamp, request_id, error_type, source, cause, context,
                       (html_snapshot IS NOT NULL) AS has_html_snapshot
                FROM error_log
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            {
                "id": row["id"],
                "timestamp": row["timestamp"],
                "request_id": row["request_id"],
                "error_type": row["error_type"],
                "source": row["source"],
                "cause": row["cause"],
                "context": json.loads(row["context"] or "{}"),
                "has_html_snapshot": bool(row["has_html_snapshot"]),
            }
            for row in rows
        ]
    except Exception as exc:  # pragma: no cover
        _logger.error(json.dumps({"level": "ERROR", "source": "error_logger.get_recent_errors", "cause": str(exc)}))
        return []


def get_error_detail(error_id: int) -> dict | None:
    """Return a single error record including the html_snapshot (if any)."""
    try:
        with _get_conn() as conn:
            _ensure_table(conn)
            row = conn.execute(
                "SELECT * FROM error_log WHERE id = ?", (error_id,)
            ).fetchone()
        if row is None:
            return None
        return {
            "id": row["id"],
            "timestamp": row["timestamp"],
            "request_id": row["request_id"],
            "error_type": row["error_type"],
            "source": row["source"],
            "cause": row["cause"],
            "context": json.loads(row["context"] or "{}"),
            "html_snapshot": row["html_snapshot"],
        }
    except Exception as exc:  # pragma: no cover
        _logger.error(json.dumps({"level": "ERROR", "source": "error_logger.get_error_detail", "cause": str(exc)}))
        return None
