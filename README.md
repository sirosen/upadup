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

`upadup` will try to update all `additional_dependencies` for all hooks.

### Configuration

`upadup` supports TOML configuration in one of two files: `.upadup.toml` or `pyproject.toml`.
These files are always checked in the current working directory.

In both cases, config is a table in `[tool.upadup]` with the following keys:

- `skip_repos`: an array of strings, exact names of repos to skip

For example:

```toml
[tool.upadup]
skip_repos = ["https://github.com/PyCQA/flake8"]
```

## The Meaning of "upadup"

Update python additional depenedencies uh... pre-commit!

Unacceptable puns accosting durable urban pachyderms

Unbelievably playful, awesome, deterministic update program
