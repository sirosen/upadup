# upadup!

`upadup` -- Utility for Python `additional_dependencies` Updates in Pre-Commit

## Why?

`pre-commit` is great, and `pre-commit autoupdate` is also great.
However, what's not great is that `pre-commit autoupdate` cannot update your
`additional_dependencies` lists.

`upadup` is a supplemental tool which knows how to handle specific common cases.

## Usage

`upadup` will only update `additional_dependencies` items which are pinned to
specific versions, and only for known python hooks and their dependencies.

Simply `cd myrepo; upadup`!

`upadup` can also be configured with information about hooks which are unknown
to it. More on this below.

### Config Loading and Format

If you have hooks outside of the defaults which you want `upadup` to examine,
drop a `.upadup.yaml` file into your repo to configure which hooks to update.

`upadup` takes no arguments and automatically reads `.upadup.yaml` from the current
directory if available.
Otherwise, it uses its default configuration.

`upadup` needs to know what hook repos you want it to examine, and within those
which dependencies you want it to keep updated.
The config format intentionally mirrors your pre-commit config. Specify a list
of repos, and in each repo, specify a list of hooks to update. Hooks are an
`id` (the hook ID) entry under the target repo.

For example:

```yaml
# .upadup.yaml
repos:
  - repo: https://github.com/pycqa/flake8
    hooks:
      - id: flake8
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

### Default Config

The following config is the `upadup` default.

```yaml
repos:
  - repo: https://github.com/pycqa/flake8
    hooks:
      - id: flake8

  - repo: https://github.com/adamchainz/blacken-docs
    hooks:
      - id: blacken-docs

  # Old hook URLs
  # -------------

  - repo: https://github.com/asottile/blacken-docs
    hooks:
      - id: blacken-docs
```

### extends_default

Unless otherwise specified, the default config will be merged with your
`.upadup.yaml` configuration, effectively a union.

You can disable this behavior by setting `extends_default: false`, as in

```yaml
extends_default: false
repos:
  - repo: https://github.com/pycqa/flake8
    hooks:
      - id: flake8
```

## The Meaning of "upadup"

Update python additional depenedencies uh... pre-commit!

Unacceptable puns accosting durable urban pachyderms

Unbelievably playful, awesome, deterministic update program
