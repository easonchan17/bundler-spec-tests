import os

from solcx import compile_source
from .types import RPCRequest, UserOperation, CommandLineArgs


def compile_contract(contract):
    current_dirname = os.path.dirname(__file__)
    contracts_dirname = current_dirname + '/contracts/'
    aa_path = os.path.realpath(current_dirname + '/../@account-abstraction')
    aa_relpath = os.path.relpath(aa_path, contracts_dirname)
    remap = '@account-abstraction=' + aa_relpath
    # print('what is dirname', contracts_dirname, aa_path, remap, aa_relpath)
    test_source = open(contracts_dirname + contract + '.sol', 'r').read()
    compiled_sol = compile_source(test_source, base_path=contracts_dirname, allow_paths=aa_relpath, import_remappings=remap, output_values=['abi', 'bin'], solc_version='0.8.15')
    return compiled_sol['<stdin>:' + contract]

def deploy_contract(w3, contract, params=[], valueEth=0, gas=10000000):
    compiled = compile_contract(contract)
    wallet = w3.eth.contract(abi=compiled['abi'], bytecode=compiled['bin'])
    account = w3.eth.accounts[0]
    tx_hash = wallet.constructor(*params).transact({'gas': gas, 'from': account, 'value': int(valueEth*10**18)})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    # print('Deployed', contract, 'contract. hash, receipt:', tx_hash.hex(), tx_receipt)
    # print(tx_receipt.contractAddress)
    return w3.eth.contract(abi=compiled['abi'], address=tx_receipt.contractAddress)

def deploy_wallet_contract(w3):
    return deploy_contract(w3, 'SimpleWallet', [CommandLineArgs.entryPoint], valueEth=0.1)

def userOpHash(wallet_contract, userOp):
    payload = (
        userOp.sender,
        int(userOp.nonce, 16),
        userOp.initCode,
        userOp.callData,
        int(userOp.callGasLimit, 16),
        int(userOp.verificationGasLimit, 16),
        int(userOp.preVerificationGas, 16),
        int(userOp.maxFeePerGas, 16),
        int(userOp.maxPriorityFeePerGas, 16),
        userOp.paymasterAndData,
        userOp.signature
    )
    return '0x' + wallet_contract.functions.getUserOpHash(payload).call().hex()


def assertRpcError(response, message, code):
    assert response.code == code
    assert message in response.message


def dumpMempool():
    mempool = RPCRequest(method='aa_dumpMempool').send().result['mempool']
    # print('what is mempool', mempool)
    for i ,entry in enumerate(mempool):
        mempool[i] = UserOperation(**entry['userOp'])
    return mempool

def clearMempool():
    mempool = RPCRequest(method='aa_clearMempool').send().result['mempool']
    # print('what is mempool', mempool)
    for i ,entry in enumerate(mempool):
        mempool[i] = UserOperation(**entry['userOp'])
    return mempool
