from webcontent import *
import pandas as pd
import requests
from tqdm import tqdm

import warnings
warnings.filterwarnings("ignore", message=r"\[W008\]", category=UserWarning)

df = pd.read_csv("../data/token_ipfs.csv")
for index, row in tqdm(df.iterrows(),  total=df.shape[0]):
    try:
        tqdm.write(f"{row['URI']} {row['ipfs']}")
        # directory = client.ls(row["ipfs"], timeout=TIMEOUT)
        # directory = list(filter(lambda x: x["Name"] == "index.html", directory.as_json()[
        #                  "Objects"][0]["Links"]))
        # cid = directory[0]["Hash"]
        # client.get(cid, timeout=TIMEOUT)
        URI = row["ipfs"]
        url = f"https://ipfs.io/ipfs/{URI}/"
        # resp = requests.get(url)
        # print(resp.text)
        data = {"URI": row["URI"]}
        r = classify_web(f"http://ipfs.io/ipfs/{URI}/")
        data.update(r)
        pd.DataFrame([data]).to_csv("../data/similarity.csv",
                                    index=False, header=False, mode="a")
        # tqdm.write(r)

    except Exception as e:
        tqdm.write(str(e))
    # input()
