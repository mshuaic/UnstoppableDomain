from hexbytes import HexBytes
from web3 import Web3


def namehash(name):
    if not name:
        return HexBytes("0"*64)
    name = name.split(".")
    label, remainder = name[0], name[1:]
    labelHash = Web3.keccak(text=label)
    remainderHash = namehash(".".join(remainder))
    return Web3.keccak(remainderHash+labelHash)
