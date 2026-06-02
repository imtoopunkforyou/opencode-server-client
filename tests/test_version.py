from opencode_server_client.version import (
    AUTHOR,
    AUTHOR_EMAIL,
    LICENSE,
    NAME,
    VERSION,
    get_package_information,
)


def test_constants_are_non_empty_strings():
    """Every exported metadata constant is a non-empty string."""
    for value in (NAME, VERSION, AUTHOR, AUTHOR_EMAIL, LICENSE):
        assert isinstance(value, str)
        assert value


def test_get_package_information_returns_expected_keys():
    """The info dict exposes exactly the documented metadata keys."""
    info = get_package_information()

    assert set(info.keys()) == {
        'name',
        'version',
        'author',
        'author_email',
        'license',
    }


def test_get_package_information_matches_constants():
    """The info dict values mirror the module-level constants."""
    info = get_package_information()

    assert info == {
        'name': NAME,
        'version': VERSION,
        'author': AUTHOR,
        'author_email': AUTHOR_EMAIL,
        'license': LICENSE,
    }


def test_get_package_information_values_are_strings():
    """Every value in the info dict is a string."""
    info = get_package_information()

    for value in info.values():
        assert isinstance(value, str)
