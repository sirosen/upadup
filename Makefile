PKG_VERSION=$(shell grep '^version' pyproject.toml | head -n1 | cut -d '"' -f2)

.PHONY: showvars release
showvars:
	@echo "PKG_VERSION=$(PKG_VERSION)"
release:
	git tag -s "$(PKG_VERSION)" -m "v$(PKG_VERSION)"
	-git push $(shell git rev-parse --abbrev-ref @{push} | cut -d '/' -f1) refs/tags/$(PKG_VERSION)
