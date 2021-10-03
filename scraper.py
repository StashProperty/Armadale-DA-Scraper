import datetime
from bs4 import BeautifulSoup
import requests
from sqlalchemy import create_engine
import pandas as pd

DATABASE = "data.sqlite"
DATA_TABLE = "data"

engine = create_engine(f'sqlite:///{DATABASE}', echo=False)

raw = requests.get("https://www.armadale.wa.gov.au/public-notices-out-comment")
soup = BeautifulSoup(raw.content, 'html.parser')
table = soup.find_all("div",class_='view-content')[1]
row_list  = table.find("tbody").find_all("tr")

today = datetime.datetime.strftime(datetime.datetime.now(),"%d-%m-%Y")
da_set = []

for row in row_list:
	cells = row.find_all("td")
	description = cells[0].text.strip().split(" - ")
	if description[0] == "Application for Development Approval":
		da = {}
		da['council_reference'] = 0
		da['description'] = " - ".join(description)
		da['address'] = description[-1]
		da['date_scraped'] = today
		da_set.append(da)

data = pd.DataFrame(da_set)
data.to_sql(DATA_TABLE, con=engine, if_exists='append',index=False)
