"""Tests for Celery task configuration and execution."""

import pytest

from capstone_core.celery_app import celery_app
from capstone_core.tasks import process_report


def test_celery_uses_redis() -> None:
    assert celery_app.conf.broker_url.startswith("redis://")
    assert celery_app.conf.result_backend.startswith("redis://")


def test_report_processing() -> None:
    result = process_report.run("report-123")

    assert result == {
        "report_id": "report-123",
        "status": "processed",
    }


def test_empty_report_id_rejected() -> None:
    with pytest.raises(ValueError):
        process_report.run("   ")


def test_task_registered() -> None:
    assert process_report.name == "capstone_core.process_report"
