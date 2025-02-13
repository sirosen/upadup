# Releasing

* Update version number and with

```sh
./scripts/bump-version.py $NEW
```

* Add, commit, and push, `git commit -m 'Bump version and changelog for release'`

* Build and publish to test-pypi by tagging, `make release`

* Build and publish to pypi by creating a github release, `gh release create`
