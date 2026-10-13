"""Tests for the httpx request-URL redaction installed by ``config.py``.

The contract under test: once ``config`` is imported, every httpx
``HTTP Request:`` line still reaches the log, with its method, path, and
status, but no URL query string. The lines must survive because
``scripts/wait_for_run.py`` reads a batch leg's log age as its liveness
signal; the query strings must go because run logs are committed to a
public repository, and a secret scanner flagged the Gemini ``pageToken``
cursors in them (2026-10-10).

The end-to-end tests drive real ``httpx`` requests through a mock
transport, so a change to httpx's own log format would show here. Each
redaction test is paired with a positive control that removes the filter
and sees the query string logged, which proves the capture is live.
"""
from __future__ import annotations

import logging
import sys
from collections.abc import Iterator
from pathlib import Path

import httpx
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config  # noqa: E402

pytestmark = pytest.mark.tier1

CURSOR = "CURSORTOKEN0123456789abcdef"
FILES_URL = f"https://generativelanguage.googleapis.com/v1alpha/files?pageToken={CURSOR}"
UPLOAD_URL = (
    "https://generativelanguage.googleapis.com/upload/v1beta/files"
    "?upload_id=UPLOADSESSION42&upload_protocol=resumable"
)
BATCH_URL = "https://generativelanguage.googleapis.com/v1alpha/batches/abc123"


def _httpx_lines(caplog: pytest.LogCaptureFixture, *urls: str) -> list[str]:
    """Issue one GET per URL through httpx and return the httpx log messages."""
    transport = httpx.MockTransport(lambda request: httpx.Response(200))
    with caplog.at_level(logging.INFO, logger="httpx"):
        with httpx.Client(transport=transport) as client:
            for url in urls:
                client.get(url)
    return [r.getMessage() for r in caplog.records if r.name == "httpx"]


@pytest.fixture
def without_redaction() -> Iterator[None]:
    """Remove the redaction filters for one test, then restore them."""
    logger = logging.getLogger("httpx")
    removed = [f for f in logger.filters if isinstance(f, config.RedactUrlQueryFilter)]
    for f in removed:
        logger.removeFilter(f)
    try:
        yield
    finally:
        for f in removed:
            logger.addFilter(f)


def _n_redaction_filters(logger_name: str) -> int:
    """Count the redaction filters attached to one logger."""
    filters = logging.getLogger(logger_name).filters
    return sum(isinstance(f, config.RedactUrlQueryFilter) for f in filters)


def test_import_installs_exactly_one_filter_on_httpx() -> None:
    """Importing config, and nothing else, attaches one filter to httpx.

    No test installs on the httpx logger itself: a filter added here would
    persist into the later tests and hide a config that never installed one.
    """
    assert _n_redaction_filters("httpx") == 1


def test_install_is_idempotent() -> None:
    """A second install on the same logger adds no second filter."""
    name = "test-http-log-redaction-idempotence"
    config.install_http_log_redaction((name,))
    config.install_http_log_redaction((name,))
    assert _n_redaction_filters(name) == 1


def test_httpx_request_line_keeps_method_path_and_status(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A paginated list request is logged with its query replaced, nothing else."""
    (line,) = _httpx_lines(caplog, FILES_URL)
    assert CURSOR not in line
    assert line == (
        "HTTP Request: GET https://generativelanguage.googleapis.com/v1alpha/files"
        '?<redacted> "HTTP/1.1 200 OK"'
    )


def test_every_query_parameter_is_redacted(caplog: pytest.LogCaptureFixture) -> None:
    """A multi-parameter upload URL loses its whole query string."""
    (line,) = _httpx_lines(caplog, UPLOAD_URL)
    assert "UPLOADSESSION42" not in line
    assert "upload_protocol" not in line
    assert "/upload/v1beta/files?<redacted>" in line


def test_url_without_query_is_unchanged(caplog: pytest.LogCaptureFixture) -> None:
    """A batch poll keeps its full line: the liveness signal is untouched."""
    (line,) = _httpx_lines(caplog, BATCH_URL)
    assert line == f'HTTP Request: GET {BATCH_URL} "HTTP/1.1 200 OK"'


def test_positive_control_query_is_logged_without_the_filter(
    caplog: pytest.LogCaptureFixture, without_redaction: None,
) -> None:
    """Without the filter the cursor reaches the log, so the capture is live."""
    (line,) = _httpx_lines(caplog, FILES_URL)
    assert CURSOR in line


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ("see https://h/p?key=K1 now", "see https://h/p?<redacted> now"),
        (
            '"https://h/a?x=1" and https://h/b?y=2',
            '"https://h/a?<redacted>" and https://h/b?<redacted>',
        ),
        ("https://h/p?q=1#frag", "https://h/p?<redacted>#frag"),
        ("no url here?really", "no url here?really"),
        ("https://h/p?", "https://h/p?<redacted>"),
    ],
)
def test_filter_text_cases(message: str, expected: str) -> None:
    """The filter redacts every URL query in a message and leaves other text alone."""
    record = logging.LogRecord("httpx", logging.INFO, __file__, 1, message, None, None)
    assert config.RedactUrlQueryFilter().filter(record) is True
    assert record.getMessage() == expected


def test_percent_in_redacted_text_is_not_reformatted() -> None:
    """After redaction the record holds final text; a literal % must survive."""
    record = logging.LogRecord(
        "httpx", logging.INFO, __file__, 1, "GET %s 100%%", ("https://h/p?q=1",), None,
    )
    config.RedactUrlQueryFilter().filter(record)
    assert record.getMessage() == "GET https://h/p?<redacted> 100%"
