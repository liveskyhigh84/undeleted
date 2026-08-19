import time

from taskguardian import config, license


def test_no_gumroad_product_id_means_unlicensed_dev_mode(monkeypatch):
    monkeypatch.setattr(config, "GUMROAD_PRODUCT_ID", None)

    assert license.is_licensed() is True


def test_missing_license_key_fails_when_gating_enabled(monkeypatch):
    monkeypatch.setattr(config, "GUMROAD_PRODUCT_ID", "prod_123")
    monkeypatch.setattr(config, "LICENSE_KEY", None)

    assert license.is_licensed() is False


def test_valid_gumroad_response_grants_access(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "GUMROAD_PRODUCT_ID", "prod_123")
    monkeypatch.setattr(config, "LICENSE_KEY", "valid-key")
    monkeypatch.setattr(license, "CACHE_PATH", tmp_path / "cache.json")
    monkeypatch.setattr(license, "_verify_with_gumroad", lambda: True)

    assert license.is_licensed() is True


def test_invalid_gumroad_response_denies_access(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "GUMROAD_PRODUCT_ID", "prod_123")
    monkeypatch.setattr(config, "LICENSE_KEY", "bad-key")
    monkeypatch.setattr(license, "CACHE_PATH", tmp_path / "cache.json")
    monkeypatch.setattr(license, "_verify_with_gumroad", lambda: False)

    assert license.is_licensed() is False


def test_network_failure_falls_back_to_grace_period_on_valid_cache(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "GUMROAD_PRODUCT_ID", "prod_123")
    monkeypatch.setattr(config, "LICENSE_KEY", "valid-key")
    monkeypatch.setattr(license, "CACHE_PATH", tmp_path / "cache.json")
    license._write_cache(True)
    future = time.time() + license.RECHECK_SECONDS + 1
    monkeypatch.setattr(license.time, "time", lambda: future)
    monkeypatch.setattr(license, "_verify_with_gumroad", lambda: None)

    assert license.is_licensed() is True


def test_network_failure_denies_access_outside_grace_period(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "GUMROAD_PRODUCT_ID", "prod_123")
    monkeypatch.setattr(config, "LICENSE_KEY", "valid-key")
    monkeypatch.setattr(license, "CACHE_PATH", tmp_path / "cache.json")
    license._write_cache(True)
    future = time.time() + license.OFFLINE_GRACE_SECONDS + 1
    monkeypatch.setattr(license.time, "time", lambda: future)
    monkeypatch.setattr(license, "_verify_with_gumroad", lambda: None)

    assert license.is_licensed() is False
