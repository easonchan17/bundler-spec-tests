import pytest
from jsonschema import validate, Validator
from tests.types import RPCRequest, CommandLineArgs
from web3 import Web3


@pytest.mark.parametrize("schema_method", ["eth_supportedEntryPoints"], ids=[""])
def test_eth_supportedEntryPoints(schema):
    response = RPCRequest(method="eth_supportedEntryPoints").send(CommandLineArgs.url)
    supported_entrypoints = response.result
    assert len(supported_entrypoints) == 1
    assert Web3.toChecksumAddress(supported_entrypoints[0]) == CommandLineArgs.entrypoint
    Validator.check_schema(schema)
    validate(instance=response.result, schema=schema)
