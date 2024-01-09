# Setup
import json
import time

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from solcx import compile_source, install_solc
from web3 import Web3

# Update me: set up my Alchemy API endpoint, CoinMarketCap API key, and test account info from Metamask wallet.
alchemy_url = "https://eth-sepolia.g.alchemy.com/v2/VI97KF1eBtVSp9k-G9PG6kadblMfrHRN"
CMC_API = "8845f199-2831-4c24-875c-f02ce65b8d50"
my_account = "0xAD0D35fD496C6F3569563f97A36AB33108BbB749"
private_key = "your-ethereum-private-keyf1b556ec6025bfe044910cccd0f08e0eadaa7c237e61856558b016caaacbbf10"
# Update me: write a MyOracle contract.
MyOracleSource = "/Users/bhavyadivecha/Downloads/ccmp606_assignment_2 2/contracts/MyOracle.sol"

def get_eth_price():
    # Update me: Fill in the CoinMarketCap API URL and headers.
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    parameters = {
        'symbol': 'ETH'
    }
    headers = {
        'X-CMC_PRO_API_KEY': CMC_API
    }

    session = Session()
    session.headers.update(headers

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

    eth_in_usd = data['data']['ETH']['quote']['USD']['price']
    return eth_in_usd

def compile_contract(w3):
    # This function is complete (no updates needed) and will compile your MyOracle.sol contract.
    with open(MyOracleSource, 'r') as file:
        oracle_code = file.read()

    compiled_sol = compile_source(
        oracle_code,
        output_values=['abi', 'bin']
    )

    # Retrieve the contract interface
    contract_id, contract_interface = compiled_sol.popitem()

    # get bytecode binary and abi
    bytecode = contract_interface['bin']
    abi = contract_interface['abi']

    Contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    print("Compile completed!")
    return Contract 

def deploy_oracle(w3, contract):
    # Update the transaction with appropriate gas, gasPrice, nonce, etc.
    deploy_txn = contract.constructor().build_transaction({
        "gas": 2000000,  # Replace with an appropriate gas limit
        "gasPrice": w3.toWei('30', 'gwei'),  # Replace with an appropriate gas price
        "nonce": w3.eth.getTransactionCount(w3.eth.default_account),
    })

    signed_txn = w3.eth.account.sign_transaction(deploy_txn, private_key=private_key)
    print("Deploying Contract...")
   
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

    txn_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    oracle_address = txn_receipt["contractAddress"]
    return oracle_address

def update_oracle(w3, contract, ethprice):
    set_txn = contract.functions.setETHUSD(ethprice).build_transaction({
        "gas": 200000,  # Replace with an appropriate gas limit
        "gasPrice": w3.toWei('30', 'gwei'),  # Replace with an appropriate gas price
        "nonce": w3.eth.getTransactionCount(w3.eth.default_account),
    })

    signed_txn = w3.eth.account.sign_transaction(set_txn, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

    txn_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return txn_receipt

def main():
    # Install Solidity compiler and connect to Alchemy endpoint.
    install_solc('0.8.17')
    w3 = Web3(Web3.HTTPProvider(alchemy_url))
    w3.eth.default_account = my_account

    # Check if connected to the endpoint
    if not w3.isConnected():
        print('Not connected to Alchemy endpoint')
        exit(-1)

    # Compile and deploy contract.
    MyOracle = compile_contract(w3)
    MyOracle.address = deploy_oracle(w3, MyOracle)
    print("My oracle address:", MyOracle.address)

    # Set up an event filter for your contract
    def setup_event_filter(w3, contract):
        event_filter = contract.events.YourEvent.createFilter(fromBlock="latest")
        return event_filter

    event_filter = setup_event_filter(w3, MyOracle)

    while True:
        print("Waiting for an oracle update request...")
        for event in event_filter.get_new_entries():
            if event.event == "YourEvent":  # Replace with your event name
                print("------------------------------------------")
                print("Callback found:")
                ETH_price = get_eth_price()
                print("Pulled Current ETH price:", ETH_price)
                print("Writing to blockchain...")
                txn = update_oracle(w3, MyOracle, ETH_price)
                print("Transaction complete!")
                print("blockNumber:", txn.blockNumber, "gasUsed:", txn.gasUsed)
                print("------------------------------------------")
        time.sleep(2)

if __name__ == "__main__":
    main()
