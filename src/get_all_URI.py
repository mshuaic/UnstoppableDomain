import requests
from ratelimit import limits
from web3 import Web3
import logging
import json
import pandas as pd
from tqdm import tqdm, trange
import asyncio

# gateway_rpc = "https://mainnet.infura.io/v3/ba8fdd8bbb6d44529e0ac13790731051"
gateway_rpc = "https://api.zmok.io/mainnet/bkl6y3afer1mr7ql"
w3 = Web3(Web3.HTTPProvider(gateway_rpc))


ud_address = "0xD1E5b0FF1287aA9f9A268759062E4Ab08b9Dacbe"
ud_abi = json.load(open("ud.abi"))

ud = w3.eth.contract(address=ud_address, abi=ud_abi)

df = pd.read_csv("transfers.csv")
burned = df[df["to"] == "0x0000000000000000000000000000000000000000"]["tokenId"]
df = df[~df["tokenId"].isin(burned)]

URIs = []

payload = {}
headers = {
    'Authorization': 'Bearer po3mnlDzOKGvgt926uB9htouov22TSJK'
}


processed = pd.read_csv("URIs.csv", names=["tokenId", "domainname", "records"])


@limits(calls=25, period=1)
def getURI(token):
    return ud.functions.tokenURI(int(token)).call()


async def write2csv(data):
    pd.DataFrame(data).to_csv("URIs.csv", index=False, header=False, mode="a")
    # json.dump(data, open("URIs.json", "a"))


async def main():
    fp = open("URI.json", "w")
    for token in tqdm(pd.unique(df[~df["tokenId"].isin(processed["tokenId"])]["tokenId"])):
        try:
            URI = getURI(token)
            domainname = URI.split('/')[-1]
            # tqdm.write(f"{token=}, {domainname=}")
            # url = f"https://unstoppabledomains.g.alchemy.com/domains/{domainname}"
            url = URI
            response = requests.request(
                "GET", url, headers=headers, data=payload)

            r = response.json()["properties"]["records"]
            asyncio.create_task(
                write2csv([{"tokenId": token, "URI": domainname, "records": r}]))
        except Exception as e:
            tqdm.write(str(e))
            tqdm.write(token)

asyncio.run(main())
