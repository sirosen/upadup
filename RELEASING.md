# Releasing

* Update version number and changelog with

```sh
hatch version $NEW
$EDITOR CHANGELOG.md
```

* Add, commit, and push, `git commit -m 'Bump version and changelog for release'`

* Build and publish with

```sh
make build
make publish-from-pypirc
```
