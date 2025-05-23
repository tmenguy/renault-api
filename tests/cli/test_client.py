"""Test cases for the __main__ module."""

import os

from aioresponses import aioresponses
from click.testing import CliRunner
from syrupy.assertion import SnapshotAssertion

from tests import fixtures
from tests.const import TEST_LOCALE
from tests.const import TEST_LOGIN_TOKEN
from tests.const import TEST_PASSWORD
from tests.const import TEST_PERSON_ID
from tests.const import TEST_USERNAME

from renault_api.cli import __main__
from renault_api.cli.renault_settings import CREDENTIAL_PATH
from renault_api.const import CONF_LOCALE
from renault_api.credential import Credential
from renault_api.credential import JWTCredential
from renault_api.credential_store import FileCredentialStore
from renault_api.gigya import GIGYA_JWT
from renault_api.gigya import GIGYA_LOGIN_TOKEN
from renault_api.gigya import GIGYA_PERSON_ID


def test_login_prompt(
    mocked_responses: aioresponses, cli_runner: CliRunner, snapshot: SnapshotAssertion
) -> None:
    """It exits with a status code of zero."""
    fixtures.inject_gigya_login(mocked_responses)

    result = cli_runner.invoke(
        __main__.main,
        "login",
        input=f"{TEST_USERNAME}\n{TEST_PASSWORD}\n{TEST_LOCALE}\ny",
    )
    assert result.exit_code == 0, result.exception
    assert result.output == snapshot


def test_login_no_prompt(
    mocked_responses: aioresponses, cli_runner: CliRunner, snapshot: SnapshotAssertion
) -> None:
    """It exits with a status code of zero."""
    fixtures.inject_gigya_login(mocked_responses)

    result = cli_runner.invoke(
        __main__.main,
        f"--locale {TEST_LOCALE} "
        f"login --user {TEST_USERNAME} --password {TEST_PASSWORD}",
    )
    assert result.exit_code == 0, result.exception
    assert result.output == snapshot


def test_list_accounts_prompt(
    mocked_responses: aioresponses, cli_runner: CliRunner, snapshot: SnapshotAssertion
) -> None:
    """It exits with a status code of zero."""
    fixtures.inject_gigya_all(mocked_responses)
    fixtures.inject_get_person(mocked_responses)

    result = cli_runner.invoke(
        __main__.main,
        "accounts",
        input=f"{TEST_LOCALE}\nN\n{TEST_USERNAME}\n{TEST_PASSWORD}\n",
    )
    assert result.exit_code == 0, result.exception
    assert result.output == snapshot


def test_list_accounts_no_prompt(
    mocked_responses: aioresponses, cli_runner: CliRunner, snapshot: SnapshotAssertion
) -> None:
    """It exits with a status code of zero."""
    credential_store = FileCredentialStore(os.path.expanduser(CREDENTIAL_PATH))
    credential_store[CONF_LOCALE] = Credential(TEST_LOCALE)
    credential_store[GIGYA_LOGIN_TOKEN] = Credential(TEST_LOGIN_TOKEN)
    credential_store[GIGYA_PERSON_ID] = Credential(TEST_PERSON_ID)
    credential_store[GIGYA_JWT] = JWTCredential(fixtures.get_jwt())

    fixtures.inject_get_person(mocked_responses)

    result = cli_runner.invoke(__main__.main, "accounts")
    assert result.exit_code == 0, result.exception
    assert result.output == snapshot
