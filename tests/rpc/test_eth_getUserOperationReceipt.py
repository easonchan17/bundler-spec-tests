import pytest
from jsonschema import validate, Validator

from tests.types import RPCRequest
from tests.utils import userop_hash, assert_rpc_error
import time


@pytest.mark.usefixtures("execute_user_operation")
@pytest.mark.parametrize("schema_method", ["eth_getUserOperationReceipt"], ids=[""])
def test_eth_getUserOperationReceipt(helper_contract, userop, w3, schema):
    time.sleep(3)
    response = RPCRequest(
        method="eth_getUserOperationReceipt",
        params=[userop_hash(helper_contract, userop)],
    ).send()
    assert response.result["userOpHash"] == userop_hash(helper_contract, userop)
    receipt = w3.eth.get_transaction_receipt(
        response.result["receipt"]["transactionHash"]
    )
    assert response.result["receipt"]["blockHash"] == receipt["blockHash"].hex()
    Validator.check_schema(schema)
    validate(instance=response.result, schema=schema)


def test_eth_getUserOperationReceipt_error():
    time.sleep(3)
    response = RPCRequest(method="eth_getUserOperationReceipt", params=[""]).send()
    assert_rpc_error(response, "Missing/invalid userOpHash", -32601)
