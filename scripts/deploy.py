from scripts.helpful_scripts import get_account, get_contract
from brownie import config, network, DappToken, TokenFarm
from web3 import Web3
import yaml
import json
import os
import shutil

KEPT_BALANCE = Web3.toWei(100, "ether")


def deploy_token_farm_and_dapp_token(front_end_update=False):
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

    if front_end_update:
        update_front_end()

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


def update_front_end():
    # Send the build folder
    copy_folder_to_front_end("./build", "./front_end/src/chain-info")
    # Sending the front end our config in JSON format
    with open("brownie-config.yaml", "r") as brownie_config:
        config_dict = yaml.load(brownie_config, Loader=yaml.FullLoader)
        with open("./front_end/src/brownie-config.json", "w") as brownie_config_json:
            json.dump(config_dict, brownie_config_json)
    print("Front end updated!")


def copy_folder_to_front_end(src, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def main():
    deploy_token_farm_and_dapp_token(front_end_update=True)
