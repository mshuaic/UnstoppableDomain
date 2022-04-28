import json
import ipfshttpclient
from functools import wraps
import pandas as pd
from tqdm import tqdm
import requests
from web3 import Web3
import time
from Utils import namehash

topics = ["automotive", "travel", "science", "technology",
          "nature", "sports", "business", "beauty", "fashion", "music", "art",
          "movie", "entertainment", "media", "children", "health", "gambling",
          "religion", "education", "politics", "history", "war", "news",
          "food", "literature", "crime"]

df_valid = pd.read_csv("../data/similarity.csv",
                       names=["domain"]+topics+["isTemplate"])
df_not_empty = df_valid[(df_valid[topics] != 0).any(
    axis=1)].reset_index(drop=True)
result = df_not_empty[df_not_empty["isTemplate"] == False].drop_duplicates()


token_ipfs = pd.read_csv("../data/token_ipfs.csv")
valid_ipfs = token_ipfs.merge(result, left_on="URI", right_on="domain")[
    ["domain", "ipfs"]]

header = ["domain",
          "remote name resolution",
          "local name resolution",
          "remote ipfs gateway",
          "local ipfs gateway"]
# pd.DataFrame([{k: None for k in header}]).to_csv(
#     "../data/elapsed/all.csv", index=False, )

# gateway_rpc = "https://api.zmok.io/mainnet/bkl6y3afer1mr7ql"
gateway_rpc_remote = "https://mainnet.infura.io/v3/ba8fdd8bbb6d44529e0ac13790731051"
web3_remote = Web3(Web3.HTTPProvider(gateway_rpc_remote))

ud_address = "0xD1E5b0FF1287aA9f9A268759062E4Ab08b9Dacbe"
ud_abi = json.load(open("../data/ud.abi"))
register_remote = web3_remote.eth.contract(address=ud_address, abi=ud_abi)

gateway_rpc_local = "http://localhost:8545"
web3_local = Web3(Web3.HTTPProvider(gateway_rpc_local))
register_local = web3_local.eth.contract(address=ud_address, abi=ud_abi)

resolver_abi = json.load(open("../data/resolver.abi"))


def elapsed(func):
    @wraps(func)
    def wrapper(*arg, **kw):
        start = time.time()
        time_elapsed = -1
        ret = None
        try:
            ret = func(*arg, **kw)
            time_elapsed = time.time() - start
        except Exception as e:
            print(e)
        return ret, time_elapsed
    return wrapper


@elapsed
def alchemy_name_resolution(domain):
    url = f"https://unstoppabledomains.g.alchemy.com/domains/{domain}"

    payload = {}
    headers = {
        'Authorization': 'Bearer po3mnlDzOKGvgt926uB9htouov22TSJK'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return response.json()["records"]["ipfs.html.value"]


@elapsed
def local_nanme_resolution(domain, register, web3):
    tokenId = int(namehash(domain).hex(), 16)
    resolver_address = register.functions.resolverOf(tokenId).call()

    resolver = web3.eth.contract(address=resolver_address, abi=resolver_abi)
    return resolver.functions.get("ipfs.html.value", tokenId)


client = ipfshttpclient.connect()


@elapsed
def local_ipfs_gateway(cid):
    r = client.ls(cid, timeout=10)
    index_page = list(filter(lambda x: x["Name"] == "index.html",
                             r.as_json()["Objects"][0]["Links"]))
    client.get(index_page[0]["Hash"], timeout=10)


@elapsed
def remote_ipfs_gateway(cid):
    url = f'https://ipfs.io/ipfs/{cid}/'
    resp = requests.get(url, timeout=10)


for _, row in tqdm(valid_ipfs.iterrows(), total=valid_ipfs.shape[0]):
    tqdm.write(str(row))

    cid, remote_name_resolution_elapsed = alchemy_name_resolution(
        row["domain"])

    _, local_name_resolution_remote_rpc_elapsed = local_nanme_resolution(
        row["domain"], register_remote, web3_remote)

    _, local_name_resolution_local_rpc_elapsed = local_nanme_resolution(
        row["domain"], register_local, web3_local)

    _, remote_ipfs_gateway_elapsed = remote_ipfs_gateway(cid)

    _, local_ipfs_gateway__elapsed = local_ipfs_gateway(cid)

    df = pd.DataFrame([{"domain": row["domain"],
                        "remote name resolution":  remote_name_resolution_elapsed,
                        "local name resolution_remote rpc": local_name_resolution_remote_rpc_elapsed,
                        "local name resolution_local rpc": local_name_resolution_local_rpc_elapsed,
                        "remote ipfs gateway": remote_ipfs_gateway_elapsed,
                        "local ipfs gateway": local_ipfs_gateway__elapsed}])
    df.to_csv("../data/elapsed/all.csv",
              index=False, header=False, mode="a")
