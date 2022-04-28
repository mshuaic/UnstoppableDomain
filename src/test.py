from web3 import Web3
import json
import pandas as pd
from tqdm import tqdm, trange
import asyncio

# gateway_rpc = "https://mainnet.infura.io/v3/ba8fdd8bbb6d44529e0ac13790731051"
# gateway_rpc = "https://api.zmok.io/mainnet/bkl6y3afer1mr7ql"
gateway_rpc = "http://localhost:8545"
w3 = Web3(Web3.HTTPProvider(gateway_rpc))


ud_address = "0xD1E5b0FF1287aA9f9A268759062E4Ab08b9Dacbe"
ud_abi = json.load(open("ud.abi"))

ud = w3.eth.contract(address=ud_address, abi=ud_abi)

df = pd.read_csv("transfers.csv")
burned = df[df["to"] == "0x0000000000000000000000000000000000000000"]["tokenId"]
df = df[~df["tokenId"].isin(burned)]

for token in tqdm(pd.unique(df["tokenId"])):
    URI = ud.functions.tokenURI(int(token)).call()
    tqdm.write(f"{token=}, {URI.split('/')[-1]=}")
    # URIs += {"tokenId": token, "URI": URI},
    pd.DataFrame([{"tokenId": token, "URI": URI}]).to_csv(
        "URIs1.csv", index=False, header=False, mode="a")
