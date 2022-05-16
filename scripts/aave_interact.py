from scripts.helpfulFunctions import getAccount, LOCAL_BLOCKCHAINS
from brownie import config, network, interface
from scripts.getWETH import getWETH
from web3 import Web3

amount = Web3.toWei(0.1, "ether")


def main():
    account = getAccount()
    erc20_address = config["networks"][network.show_active()]["weth_erc20"]
    if network.show_active() in LOCAL_BLOCKCHAINS:
        getWETH()

    lending_pool = get_lending_pool()
    print(lending_pool)
    # Approve sending out ERC20 tokens
    approve_erc20(amount, lending_pool.address, erc20_address, account)
    print("Depositing ...")
    tx = lending_pool.deposit(
        erc20_address,
        amount,
        account.address,
        0,
        {"from": account, "gas_limit": 1000000000},
    )
    tx.wait(1)
    print("Deposited!")

    # ... how much to borrow?
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
    print("Let's borrow!")
    # USDT in terms of ETH
    usdt_eth_price = get_asset_price(
        config["networks"][network.show_active()]["usdt_eth_price_feed"]
    )
    amount_usdt_to_borrow = (1 / usdt_eth_price) * (borrowable_eth * 0.95)
    # borrowable_eth -> borrowable_usdt * 95%
    print(f"We are going to borrow {amount_usdt_to_borrow} USDT")

    # Now we will borrow!
    usdt_address = config["networks"][network.show_active()]["usdt_erc20"]
    borrow_tx = lending_pool.borrow(
        usdt_address,
        Web3.toWei(amount_usdt_to_borrow, "ether"),
        1,
        0,
        account.address,
        {"from": account},
    )
    borrow_tx.wait(1)
    print("We borrowed some USDT!")
    get_borrowable_data(lending_pool, account)
    print(
        "We have just deposited, borrowed, and repaid with Aave, Brownie, and Chainlink!"
    )


def repay_all(amount, lending_pool, account):
    approve_erc20(
        Web3.toWei(amount, "ether"),
        lending_pool,
        config["networks"][network.show_active()]["usdt_erc20"],
        account,
    )

    repay_tx = lending_pool.repay(
        config["networks"][network.show_active()]["usdt_erc20"],
        amount,
        1,
        account,
        {"from": account},
    )
    repay_tx.wait(1)
    print("Repaid!")


def get_asset_price(price_feed_address):

    usdt_eth_price_feed = interface.AggregatorV3Interface(price_feed_address)

    latest_price = usdt_eth_price_feed.latestRoundData()[1]
    converted_latest_price = Web3.fromWei(latest_price, "ether")
    print(f"The USDT/ETH price is {converted_latest_price}")
    return float(converted_latest_price)


def get_borrowable_data(lending_pool, account):
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrow_eth,
        current_liquidation_threshold,
        ltv,
        health_factor,
    ) = lending_pool.getUserAccountData(account.address)

    # coverting from wei to eth
    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    print(f"You have {total_collateral_eth} worth of ETH deposited.")
    print(f"You have {total_debt_eth} worth of ETH borrowed.")
    print(f"You can borrow {available_borrow_eth} worth of ETH.")
    return (
        float(available_borrow_eth),
        float(total_debt_eth),
    )


def approve_erc20(amount, spender, token_address, account):
    print("Approving ERC20 token ...")
    token20 = interface.IERC20(token_address)
    tranx = token20.approve(spender, amount, {"from": account})
    tranx.wait(1)
    print("Approved!")
    return tranx


def get_lending_pool():

    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool
