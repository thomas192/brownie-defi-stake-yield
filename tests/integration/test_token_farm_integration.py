from brownie import network
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_account,
    get_contract,
)
from scripts.deploy import deploy_token_farm_and_dapp_token
import pytest


def test_stake_and_issue_correct_amounts(amount_staked):
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    account = get_account()

    print(
        f"Initial DAPP balance : {dapp_token.balanceOf(account.address) / (10 ** 18)}"
    )
    dapp_token.approve(token_farm.address, amount_staked, {"from": account})

    print("Staking DAPP...")
    tx = token_farm.stakeTokens(amount_staked, dapp_token.address, {"from": account})
    tx.wait(1)
    print("DAPP staked")

    starting_balance = dapp_token.balanceOf(account.address)
    print(f"DAPP balance after staking : {starting_balance / (10 ** 18)}")

    price_feed_contract = get_contract("dai_usd_price_feed")
    (_, price, _, _, _) = price_feed_contract.latestRoundData()
    print(f"Price feed price : {price / price_feed_contract.decimals()}")

    # Stake 1 token
    # 1 Token = $2000
    # We should be issued 2000 tokens
    amount_token_to_issue = (
        price / 10 ** price_feed_contract.decimals()
    ) * amount_staked
    print(f"Amount of tokens to issue : {amount_token_to_issue}")

    # Act
    tx = token_farm.issueTokens({"from": account})
    tx.wait(1)
    # Assert
    assert (
        dapp_token.balanceOf(account.address)
        == amount_token_to_issue + starting_balance
    )
