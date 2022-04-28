import pandas as pd
from tqdm import tqdm
import requests

top100 = pd.read_csv("../data/top-1m.csv", index_col=0,
                     names=["domain"])
count = 100

for _, row in tqdm(top100.iterrows(), total=count):
    if count == 0:
        break
    resp = None
    try:
        resp = requests.get(f'https://{row["domain"]}', timeout=10)
        tqdm.write(row['domain'])
        tqdm.write(f"{resp.status_code}")
        tqdm.write(f"{resp.elapsed}")
    except Exception as e:
        print(e)
    elapsed = resp.elapsed.total_seconds() if resp is not None else -1
    pd.DataFrame([{"domain": row["domain"],
                   "elapsed": elapsed}]).to_csv("../data/top100_elaspsed.csv",
                                                index=False, header=False, mode="a")
    count -= 1
