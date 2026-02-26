version := `uvx mddj read version`

build:
    uv build

test:
    tox p

check-sdist:
    uvx --from='check-sdist==1.3.1' check-sdist --inject-junk

tag-release:
    git tag -s "{{version}}" -m "v{{version}}"

clean:
	rm -rf dist build *.egg-info .tox .venv
	find . -type d -name '__pycache__' -exec rm -r {} +
