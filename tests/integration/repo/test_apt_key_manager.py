# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2023 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Integration tests for AptKeyManager"""
import os
from pathlib import Path

import pytest
from craft_archives.repo.apt_key_manager import AptKeyManager


@pytest.fixture
def test_keys_dir() -> Path:
    return Path(__file__).parent / "test_keys"


@pytest.fixture
def key_assets(tmp_path):
    assets = tmp_path / "key-assets"
    assets.mkdir(parents=True)
    return assets


@pytest.fixture
def gpg_keyring(tmp_path):
    return tmp_path / "keyring.gpg"


@pytest.fixture
def apt_gpg(key_assets, tmp_path):
    return AptKeyManager(
        keyrings_path=tmp_path,
        key_assets=key_assets,
    )


def test_install_key(apt_gpg, tmp_path, test_keys_dir):
    expected_file = tmp_path / "craft-FC42E99D.gpg"
    assert not expected_file.exists()
    assert not apt_gpg.is_key_installed(key_id="FC42E99D", keyring_path=tmp_path)

    keypath = test_keys_dir / "FC42E99D.asc"
    apt_gpg.install_key(key=keypath.read_text())

    assert expected_file.is_file()
    assert apt_gpg.is_key_installed(key_id="FC42E99D", keyring_path=tmp_path)


def test_install_key_from_keyserver(apt_gpg, tmp_path):
    expected_file = tmp_path / "craft-FC42E99D.gpg"
    assert not expected_file.exists()
    assert not apt_gpg.is_key_installed(key_id="FC42E99D", keyring_path=tmp_path)

    key_id = "78E1918602959B9C59103100F1831DDAFC42E99D"
    apt_gpg.install_key_from_keyserver(key_id=key_id)

    assert expected_file.is_file()
    assert apt_gpg.is_key_installed(key_id="FC42E99D", keyring_path=tmp_path)


def test_install_key_missing_directory(key_assets, tmp_path, test_keys_dir):
    keyrings_path = tmp_path / "keyrings"
    assert not keyrings_path.exists()

    apt_gpg = AptKeyManager(
        keyrings_path=keyrings_path,
        key_assets=key_assets,
    )

    keypath = test_keys_dir / "FC42E99D.asc"
    apt_gpg.install_key(key=keypath.read_text())

    assert keyrings_path.exists()
    assert os.stat(keyrings_path).st_mode == 0o40755
