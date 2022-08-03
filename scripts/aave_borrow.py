from scripts.helpful_scripts import get_account
from scripts.get_weth import get_weth
from brownie import network, config, interface
from web3 import Web3

amount = Web3.toWei(0.1, "ether")


def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    # if network.show_active() in ["mainnet-fork"]:
    get_weth()  # bc we already have WETH in kovan, only calling get weth in forked environment.
    # ABI
    # Address
    lending_pool = get_lending_pool()
    # approve sending erc20 tokens
    approve_erc20(amount, lending_pool.address, erc20_address, account)
    tx = lending_pool.deposit(
        erc20_address, amount, account.address, 0, {"from": account}
    )  # referral code is the last variable and it is deprecated. always use 0
    tx.wait(1)
    print("Deposited!")
    borrowable_eth, _, _ = get_borrowable_data(lending_pool, account)
    print("Time to borrow")
    # DAI in terms of ETH needed... use chainlink price feeds.
    dai_eth_price = get_asset_price("dai_eth")
    amount_dai_to_borrow = (1 / dai_eth_price) * (borrowable_eth * 0.95)
    dai_address = config["networks"][network.show_active()]["dai_token"]
    borrow_tx = lending_pool.borrow(
        dai_address,
        Web3.toWei(amount_dai_to_borrow, "ether"),
        1,
        0,
        account.address,
        {"from": account},
    )
    borrow_tx.wait(1)
    print("Borrowed some dai!")
    get_borrowable_data(lending_pool, account)
    # repay_all(Web3.toWei(amount_dai_to_borrow, "ether"), lending_pool, account)
    # get_borrowable_data(lending_pool, account)


def withdraw_all_eth(account, lending_pool):
    _, _, collateral = get_borrowable_data(lending_pool, account)
    tx = lending_pool.withdraw(
        config["networks"][network.show_active()]["weth_token"],
        Web3.toWei(collateral, "ether"),
        account.address,
        {"from": account},
    )
    tx.wait(1)
    print("Withdrew all eth!")
    get_borrowable_data(lending_pool, account)


def repay_all(amount, lending_pool, account):
    dai = config["networks"][network.show_active()]["dai_token"]
    approve_erc20(
        Web3.toWei(amount, "ether"),
        lending_pool,
        dai,
        account,
    )
    repay_tx = lending_pool.repay(dai, amount, 1, account.address, {"from": account})
    repay_tx.wait(1)
    print("Repaid!")


def get_asset_price(pair):
    price_feed_address = config["networks"][network.show_active()][f"{pair}_price_feed"]
    dai_eth_price_feed = interface.AggregatorV3Interface(price_feed_address)
    latest_price = dai_eth_price_feed.latestRoundData()[1]
    converted_latest_price = Web3.fromWei(latest_price, "ether")
    print(f"DAI-ETH Price is {converted_latest_price}")
    return float(converted_latest_price)


def get_borrowable_data(lending_pool, account):
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrow_eth,
        current_liquidation_threshold,
        ltv,
        health_factor,
    ) = lending_pool.getUserAccountData(account)

    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    print(f"you have {total_collateral_eth} worth of ETH deposited")
    print(f"you have {total_debt_eth} worth of ETH borrowed")
    print(f"you can borrow {available_borrow_eth} ETH")
    return (
        float(available_borrow_eth),
        float(total_debt_eth),
        float(total_collateral_eth),
    )


def get_lending_pool():
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    # ABI
    # Address
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool


def approve_erc20(amount, spender, erc20_address, account):
    print("Approving ERC20 token...")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("Approved!")
    return tx
