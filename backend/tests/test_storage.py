import pytest
from cryptography.fernet import Fernet

from app import storage
from app.config import get_settings


def test_round_trip_and_encrypted_on_disk(isolated_storage):
    data = b"%PDF-1.7 Suraksha Health Plus policy wording"
    key = storage.save(data)
    assert storage.load(key) == data
    on_disk = (isolated_storage / key).read_bytes()
    assert b"Suraksha" not in on_disk and on_disk != data


def test_dev_key_created_once(isolated_storage):
    storage.save(b"a")
    first = (isolated_storage / ".dev-key").read_text()
    storage.save(b"b")
    assert (isolated_storage / ".dev-key").read_text() == first


def test_explicit_key_is_used(isolated_storage, monkeypatch):
    monkeypatch.setattr(get_settings(), "file_encryption_key", Fernet.generate_key().decode())
    key = storage.save(b"secret")
    assert storage.load(key) == b"secret"
    assert not (isolated_storage / ".dev-key").exists()


def test_delete(isolated_storage):
    key = storage.save(b"x")
    storage.delete(key)
    assert not (isolated_storage / key).exists()
    storage.delete(key)  # deleting twice is fine


@pytest.mark.parametrize("bad", ["../secret.bin", "a/b.bin", "a\\b.bin"])
def test_rejects_path_tricks(bad):
    with pytest.raises(ValueError):
        storage.load(bad)
