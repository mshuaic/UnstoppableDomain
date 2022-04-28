import requests
from tqdm import tqdm
import pandas as pd
import json

df = pd.read_csv("../src/URIs_old.csv", names=["tokenId", "URI"])
# display(df.iloc[:5].to_dict("records"))
records = df.to_dict("records")

# print(list(items.items())[0])
token_prop = {}

for record in tqdm(records):
    tokenId = record["tokenId"]
    URI = record["URI"]
    response = requests.request("GET", URI)
    token_prop[tokenId] = response.json()["properties"]["records"]
    tqdm.write(json.dumps(token_prop[tokenId]))

json.dump(token_prop, open("token_prop.json", "w"))
