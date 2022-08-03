from scripts.aave_borrow import withdraw_all_eth, get_lending_pool
from scripts.helpful_scripts import get_account


def main():
    withdraw_all_eth(get_account(), get_lending_pool())
