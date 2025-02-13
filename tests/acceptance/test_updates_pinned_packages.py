import textwrap

import pytest


@pytest.mark.parametrize("quote_char", ("", '"', "'"))
def test_updates_package_preserving_quote_char(
    update_from_text, mock_package_latest_version, quote_char
):
    mock_package_latest_version("flake8-bugbear", "24.12.12")
    fixed_text = update_from_text(
        f"""\
        repos:
          - repo: https://github.com/PyCQA/flake8
            rev: 7.1.1
            hooks:
              - id: flake8
                additional_dependencies:
                  - {quote_char}flake8-bugbear==23.0.0{quote_char}
        """
    )
    assert fixed_text == textwrap.dedent(
        f"""\
        repos:
          - repo: https://github.com/PyCQA/flake8
            rev: 7.1.1
            hooks:
              - id: flake8
                additional_dependencies:
                  - {quote_char}flake8-bugbear==24.12.12{quote_char}
        """
    )


def test_updates_package_preserving_strange_indentation(
    update_from_text, mock_package_latest_version
):
    mock_package_latest_version("flake8-typing-as-t", "1.0.0")
    fixed_text = update_from_text(
        """\
        repos:
        - repo: https://github.com/PyCQA/flake8
          rev: 7.1.1
          hooks:
              - id: flake8
                additional_dependencies:
                            - "flake8-typing-as-t==0.0.3"
        """
    )
    assert fixed_text == textwrap.dedent(
        """\
        repos:
        - repo: https://github.com/PyCQA/flake8
          rev: 7.1.1
          hooks:
              - id: flake8
                additional_dependencies:
                            - "flake8-typing-as-t==1.0.0"
        """
    )


def test_updates_multiple_packages_in_one_line_with_length_changes(
    update_from_text, mock_package_latest_version
):
    mock_package_latest_version("flake8-typing-as-t", "1.0.0")
    mock_package_latest_version("flake8-bugbear", "24.12.12")
    mock_package_latest_version("flake8-comprehensions", "3.16.0")
    fixed_text = update_from_text(
        """\
        repos:
          - repo: https://github.com/PyCQA/flake8
            rev: 7.1.1
            hooks:
              - id: flake8
                additional_dependencies: [
                  "flake8-typing-as-t==0.0", "flake8-bugbear==23", "flake8-comprehensions==2.1"
                ]
        """  # noqa: E501
    )
    assert fixed_text == textwrap.dedent(
        """\
        repos:
          - repo: https://github.com/PyCQA/flake8
            rev: 7.1.1
            hooks:
              - id: flake8
                additional_dependencies: [
                  "flake8-typing-as-t==1.0.0", "flake8-bugbear==24.12.12", "flake8-comprehensions==3.16.0"
                ]
        """  # noqa: E501
    )


def test_updates_are_tolerant_of_spaces_around_version_comparator(
    update_from_text, mock_package_latest_version
):
    mock_package_latest_version("flake8-bugbear", "24.12.12")
    fixed_text = update_from_text(
        """\
        repos:
          - repo: https://github.com/PyCQA/flake8
            rev: 7.1.1
            hooks:
              - id: flake8
                additional_dependencies:
                  - "flake8-bugbear == 23.0.0"
        """
    )
    assert fixed_text == textwrap.dedent(
        """\
        repos:
          - repo: https://github.com/PyCQA/flake8
            rev: 7.1.1
            hooks:
              - id: flake8
                additional_dependencies:
                  - "flake8-bugbear == 24.12.12"
        """
    )


def test_updates_of_compatible_release_clauses(
    update_from_text, mock_package_latest_version
):
    mock_package_latest_version("flake8-bugbear", "24.12.12")
    fixed_text = update_from_text(
        """\
        repos:
          - repo: https://github.com/PyCQA/flake8
            rev: 7.1.1
            hooks:
              - id: flake8
                additional_dependencies:
                  - "flake8-bugbear ~= 23.0.0"
        """
    )
    assert fixed_text == textwrap.dedent(
        """\
        repos:
          - repo: https://github.com/PyCQA/flake8
            rev: 7.1.1
            hooks:
              - id: flake8
                additional_dependencies:
                  - "flake8-bugbear ~= 24.12.12"
        """
    )


def test_updates_of_arbitrary_equality_clauses(
    update_from_text, mock_package_latest_version
):
    mock_package_latest_version("flake8-bugbear", "24.12.12")
    fixed_text = update_from_text(
        """\
        repos:
          - repo: https://github.com/PyCQA/flake8
            rev: 7.1.1
            hooks:
              - id: flake8
                additional_dependencies:
                  - "flake8-bugbear === abc.def.post1-dev1"
        """
    )
    assert fixed_text == textwrap.dedent(
        """\
        repos:
          - repo: https://github.com/PyCQA/flake8
            rev: 7.1.1
            hooks:
              - id: flake8
                additional_dependencies:
                  - "flake8-bugbear === 24.12.12"
        """
    )
