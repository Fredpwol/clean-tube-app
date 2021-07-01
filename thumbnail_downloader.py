import pandas as pd
import urllib
from pathlib import Path


csv = pd.read_csv("https://docs.google.com/spreadsheets/d/10T3lIOc5fZgsyvmYeWOlmgsaRiGI2BhYNBPY5YH0EFk/export?format=csv&id=10T3lIOc5fZgsyvmYeWOlmgsaRiGI2BhYNBPY5YH0EFk&gid=0")
csv.dropna()
csv.drop_duplicates()

curr_dir = Path(__file__).parent.resolve()

for ind in csv.index:
    try:
        print(str(csv["titles"][ind]))
        file_name = str(csv["total"][ind])+"_"+str(csv["id"][ind])+".jpg"
        urllib.request.urlretrieve("https://i.ytimg.com/vi/"+str(csv["id"][ind])+"/hqdefault.jpg", curr_dir / "data" / "data_manualy_tag" / file_name)
    except Exception as e:
        print(e)
        print("error on :"+str(csv["titles"][ind]))
