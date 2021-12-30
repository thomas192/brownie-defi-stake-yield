from scripts.helpful_scripts import get_account, get_contract
from brownie import config, network, DappToken, TokenFarm
from web3 import Web3

KEPT_BALANCE = Web3.toWei(100, "ether")


def deploy_token_farm_and_dapp_token():
    account = get_account()
    print("Deploying DappToken...")
    dapp_token = DappToken.deploy({"from": account})
    print(f"Deployed DappToken.")

    print("Deploying TokenFarm...")
    token_farm = TokenFarm.deploy(
        dapp_token.address,
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print(f"Deployed TokenFarm.")

    print("Transferring DAPP to TokenFarm...")
    tx = dapp_token.transfer(
        token_farm.address, dapp_token.totalSupply() - KEPT_BALANCE, {"from": account}
    )
    tx.wait(1)
    print(f"DAPP transferred {tx.txid}")

    weth_token = get_contract("weth_token")
    fau_token = get_contract("fau_token")
    dict_of_allowed_tokens = {
        dapp_token: get_contract("dai_usd_price_feed"),
        fau_token: get_contract("dai_usd_price_feed"),
        weth_token: get_contract("eth_usd_price_feed"),
    }
    add_allowed_tokens(token_farm, dict_of_allowed_tokens, account)
    return token_farm, dapp_token


def add_allowed_tokens(token_farm, dict_of_allowed_tokens, account):
    print("Adding allowed tokens...")
    for token in dict_of_allowed_tokens:
        tx = token_farm.addAllowedTokens(token.address, {"from": account})
        tx.wait(1)
        tx = token_farm.setPriceFeedContract(
            token.address, dict_of_allowed_tokens[token], {"from": account}
        )
        tx.wait(1)
    print("All tokens added")
    return token_farm


def main():
    deploy_token_farm_and_dapp_token()
