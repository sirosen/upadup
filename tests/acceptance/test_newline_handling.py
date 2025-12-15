import itertools

import pytest

from upadup.updater import UpadupUpdater


@pytest.mark.parametrize(
    "newline_pattern",
    [
        pytest.param([b"\r\n", b"\n"], id="rn|n"),
        pytest.param([b"\n", b"\r\n"], id="n|rn"),
        pytest.param([b"\r", b"\r\n"], id="r|rn"),
        pytest.param([b"\n", b"\n", b"\r\n"], id="n|n|rn"),
        pytest.param([b"\r\n", b"\r\n", b"\n"], id="rn|rn|n"),
        pytest.param([b"\r", b"\r\n", b"\n"], id="r|rn|n"),
        pytest.param([b"\r", b"\r", b"\r", b"\n"], id="r|r|r|n"),
    ],
)
def test_updates_package_and_preserves_mixed_newlines(
    mock_package_latest_version, tmp_path, newline_pattern
):
    mock_package_latest_version("flake8-bugbear", "24.12.12")

    content = [
        b"repos:",
        b"",
        b"  - repo: https://github.com/PyCQA/flake8",
        b"    rev: 7.1.1",
        b"    hooks:",
        b"      - id: flake8",
        b"        additional_dependencies:",
        b"          - 'flake8-bugbear==23.0.0'",
    ]
    expect_fixed_content = list(content[:-1]) + [
        b"          - 'flake8-bugbear==24.12.12'"
    ]

    newline_series = itertools.cycle(newline_pattern)
    content = [line + next(newline_series) for line in content]
    newline_series = itertools.cycle(newline_pattern)  # restart the cycle
    expect_fixed_content = [
        line + next(newline_series) for line in expect_fixed_content
    ]

    conf = tmp_path / "conf.yaml"
    conf.write_bytes(b"".join(content))

    updater = UpadupUpdater(path=conf)
    updater.run()
    updater.apply_updates()

    fixed_bytes = conf.read_bytes()
    assert fixed_bytes == b"".join(expect_fixed_content)
