from scripts.helpfulFunctions import getAccount
from brownie import interface, config, network


def main():
    getWETH()


def getWETH():
    """""
    Mints WETH by depositing ETH.
    """ ""
    account = getAccount()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_erc20"])
    tranx = weth.deposit({"from": account, "value": 0.1 * (10 ** 18)})
    tranx.wait(1)
    print(f"Received 0.1 WETH")
    return tranx
