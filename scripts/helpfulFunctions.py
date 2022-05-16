from brownie import accounts, network, config

LOCAL_BLOCKCHAINS = ["development", "ganache-local", "mainnet-fork"]


def getAccount(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if network.show_active() in LOCAL_BLOCKCHAINS:
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])
