# CHANGELOG

## Unreleased

- Remove support for Python 3.9

## 0.4.0

- Fix a `NameError` crash that occurs if mixed newlines are encountered.
- Support updating Go dependencies hosted on GitHub.
- Add a `--freeze` CLI option to freeze dependencies to git SHAs.
- `upadup`'s configuration has been rewritten, and is now TOML rather than YAML.

## 0.3.1

- Avoid using `typing.Self`, which causes issues when type checking on older
  Python versions which do not define `Self` yet.

## 0.3.0

- `upadup` now supports "Compatible release" (`~=`) and "Arbitrary equality"
  (`===`) clauses when parsing dependency specifiers and will update packages
  with these styles of pins to their latest versions.
- Parsing and handling of whitespace in dependency specifiers has been
  improved. Whitespace is now handled correctly in more scenarios.

## 0.2.0

- Performance enhancement: `upadup` will only call out to `pypi.org` on an
  as-needed basis
- `upadup` no longer requires that config enumerates all of the
  `additional_dependencies` entries. Instead, it works on all
  `additional_dependencies` for the configured hooks.

## 0.1.0

- Timeout after 30 seconds when retrieving JSON from PyPI.
- Support updating dependencies associated with the canonical blacken-docs repo.

## 0.0.8

- Add `flake8-logging-format` and `flake8-implicit-str-concat` to default
  config
- Fix a crash bug when known hooks were present without the anticipated
  `additional_dependencies`
- Normalize repository names to remove trailing `.git` where appropriate, to
  enable matching in more cases

## 0.0.7

- Fix handling of unquoted string literals in "bare strings" style

## 0.0.6

- Fix handling of literal string nodes during yaml loading

## 0.0.5

- Fix handling of empty or missing `.upadup.yaml` config

## 0.0.4

- Add `flake8-typing-as-t` to default config

## 0.0.3

- Configuration now defaults to a merge between defaults and user config. This
  can be disabled with `extends_default: false`
- Configuration data is now validated before further processing

## 0.0.2

- Fix handling of multiple updates in a single line
- Fix config for known flake8 hooks
- Add a `--check` flag for getting a diff without making an update

## 0.0.1

- Initial version
