# CHANGELOG

## Unreleased

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
