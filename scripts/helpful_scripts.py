from brownie import (
    accounts,
    network,
    config,
)

from web3 import Web3

LOCAL_BLOCKCHAIN_ENVIRONMENTS = [
    "development",
    "ganache-local",
    "ganache",
    "hardhat",
    "mainnet-fork",
]


def get_account(index=0, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]

    return accounts.add(config["wallets"]["from_key"])
