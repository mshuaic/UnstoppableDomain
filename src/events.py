"""
get all transfer events.
"""

from web3 import Web3
import logging
import json
import pandas as pd
from tqdm import tqdm, trange

logging.basicConfig(
    format='%(asctime)s %(levelname)-5s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
log = logging.getLogger(__name__)


# w3 = Web3(Web3.IPCProvider('/home/markma/NFT/eth/data/geth.ipc'))
# w3.middleware_onion.inject(geth_poa_middleware, layer=0)

gateway_rpc = "https://mainnet.infura.io/v3/ba8fdd8bbb6d44529e0ac13790731051"
w3 = Web3(Web3.HTTPProvider(gateway_rpc))


ud_address = "0xD1E5b0FF1287aA9f9A268759062E4Ab08b9Dacbe"
ud_abi = json.load(open("ud.abi"))

ud = w3.eth.contract(address=ud_address, abi=ud_abi)

batch_size = 1000

startingBlock = 9082251
# currBlock =
# endblock = 9082251 + 1000
endBlock = w3.eth.block_number
# print(w3.eth.block_number)

# while currBlock < endblock:
for currBlock in trange(startingBlock, endBlock, batch_size):
    transfers = []
    event_filter = ud.events.Transfer.createFilter(
        fromBlock=currBlock, toBlock=currBlock+batch_size)
    for event in event_filter.get_all_entries():
        item = dict(event.args)
        item.update({"txhash": event.transactionHash.hex(),
                     "blockNumber": event.blockNumber})
        transfers += item,
        currBlock += batch_size
    pd.DataFrame(transfers).to_csv("transfers.csv", index=False, mode="a")


# print(ud.functions.name().call())


# # print(w3.eth.get_logs({'address': ud_address,
# #                        "fromBlock": hex(9082251)}))


# def handle_event(event):
#     # _from = event["args"]["from"]
#     # _to = event["args"]["to"]
#     # tid = event["args"]["tokenId"]
#     # tx = event["transactionHash"].hex()
#     # tURI = artopus.functions.tokenURI(tid).call()

#     log.info(event)
#     # print(event)
#     # insert to the database
#     # cur.execute("insert into TXs values (?, ?, ?, ?, ?)",
#     #             (tx, _from, _to, tid, tURI))

#     # send2db(tid, tURI, _from, _to)


# async def log_loop(event_filter, poll_interval):
#     while True:
#         for event in event_filter.get_all_entries():
#             handle_event(event)
#         await asyncio.sleep(poll_interval)


# def main():
#     event_filter = ud.events.Transfer.createFilter(
#         fromBlock=9082251, toBlock=9082251)
#     loop = asyncio.get_event_loop()
#     try:
#         loop.run_until_complete(
#             asyncio.gather(
#                 log_loop(event_filter, 2),
#             ))
#     finally:
#         loop.close()


# if __name__ == '__main__':
#     main()
# pass
