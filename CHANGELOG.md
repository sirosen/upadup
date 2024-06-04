# CHANGELOG

## Unreleased

- Timeout after 30 seconds when retrieving JSON from PyPI.

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
