import pytest
import responses


@pytest.fixture(autouse=True)
def mocked_responses():
    responses.start()

    yield

    responses.stop()
    responses.reset()


@pytest.fixture
def mock_package_latest_version(mocked_responses):
    def func(pkg, version):
        responses.get(
            f"https://pypi.python.org/pypi/{pkg}/json",
            json={"info": {"version": version}},
        )

    return func
