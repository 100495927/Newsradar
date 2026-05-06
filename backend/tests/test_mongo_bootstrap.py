from __future__ import annotations

from scripts.mongo.admin import apply_bootstrap
from shared.mongo.bootstrap_spec import COLLECTION_SPECS, COUNTER_SEEDS


def test_apply_bootstrap_imports_shared_spec() -> None:
    assert apply_bootstrap.COLLECTION_SPECS is COLLECTION_SPECS
    assert apply_bootstrap.COUNTER_SEEDS is COUNTER_SEEDS


def test_alerts_collection_bootstrap_spec_matches_runtime_expectations() -> None:
    alerts_spec = next(spec for spec in COLLECTION_SPECS if spec["name"] == "alerts")
    schema = alerts_spec["validator"]["$jsonSchema"]

    assert "category_id" in schema["required"]
    assert "rss_channel_ids" in schema["required"]
    assert "information_sources_ids" in schema["required"]
    assert "enabled" in schema["required"]
    assert schema["properties"]["next_run_at"]["bsonType"] == ["date", "null"]

    index_names = {index["kwargs"]["name"] for index in alerts_spec["indexes"]}
    assert "idx_alerts_user_enabled_next_run" in index_names
    assert "idx_alerts_rss_channel_ids" in index_names
    assert "idx_alerts_information_sources_ids" in index_names
