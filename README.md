# pudu

`pudu` -- update pre-commit `additional_dependencies`

## Why?

`pre-commit` is great, and `pre-commit autoupdate` is also great.
However, what's not great is that `pre-commit autoupdate` cannot update your
`additional_dependencies` lists.

This is a well-reasoned limitation of `pre-commit autoupdate`, and
`pudu` does not aim to change this.

It provides a supplemental tool which knows how to handle specific common cases.

## Usage

Drop a `.pudu.yaml` file into your repo to configure which hooks to update.

`pudu` takes no arguments and automatically reads `.pudu.yaml` from the current
directory if available.
Otherwise, it uses its default configuration.

### Config Format

`pudu` needs to know what hook repos you want it to examine, and within those
which dependencies you want it to keep updated.
The config format intentionally mirrors your pre-commit config. Specify a list
of repos, and in each repo, specify a list of hooks to update. Hooks are a
combination of `id` (the hook ID) and `additional_dependencies`.

For example:

```yaml
# .pudu.yaml
repos:
  - repo: https://github.com/pycqa/flake8
    hooks:
      - id: flake8
        additional_dependencies:
          - flake8_bugbear
```

This configuration would match the following pre-commit config:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/PyCQA/flake8
    rev: 5.0.4
    hooks:
      - id: flake8
        additional_dependencies:
          - 'flake8-bugbear==22.7.1'
```

Note that matching is case insensitive for repo names and
`additional_dependencies`, and that we normalize `-` and `_` to match, as
pypi.org does. But the overall structure of the config is intended to be a
mirror image.

### Default Config

The following config is the `pudu` default. Note that missing dependencies are
ignored.

```yaml
repos:
  - repo: https://github.com/pycqa/flake8
    hooks:
      - id: flake8
        additional_dependencies:
          - flake8-bandit
          - flake8-bugbear
          - flake8-comprehensions
          - flake8-pyi
          - flake8-typing-imports
          - flake8-docstrings
          - flake8-builtins
  - repo: https://github.com/asottile/blacken-docs
    hooks:
      - id: blacken-docs
        additional_dependencies:
          - black
```

## Why is it named "pudu"?

**Choose the reason which you like best.**

PUDU could be the Pre-commit UpdatUr.

A pudu is a small, cute, crepuscular deer.

PUDU might stand for Python Updating Data Utility.

"pudu" is a homophone for poodoo (as in bantha poodoo).

PUDU could be Puns Under DUress.
