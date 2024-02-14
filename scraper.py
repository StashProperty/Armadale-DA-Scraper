import datetime
from bs4 import BeautifulSoup
import requests
from sqlalchemy import Column, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

DATABASE = "data.sqlite"
DATA_TABLE = "data"

engine = create_engine(f'sqlite:///{DATABASE}', echo=False)


class DA(Base):
    __tablename__ = DATA_TABLE

    council_reference = Column(String, primary_key=True)
    description = Column(String)
    address = Column(String)
    date_received = Column(String)
    date_scraped = Column(String)


Base.metadata.create_all(engine)

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

raw = requests.get("https://www.armadale.wa.gov.au/community-consultation")
soup = BeautifulSoup(raw.content, 'html.parser')
row_list = soup.select("table:has(caption h3:-soup-contains('Development Applications')) tr")

da_set = []
today = datetime.datetime.strftime(datetime.datetime.now(), "%m-%d-%Y")

for row in row_list:
    cells = row.find_all("td")
    if not cells:
        # skip header row
        continue
    description = cells[0].text.strip().split(" - ")
    slug = cells[0].find("a")['href'].split("/")[-1]

    da = session.get(DA, slug)
    if not da:
        da = DA(council_reference=slug, date_received=today)
        session.add(da)
    da.description = "- ".join(description)
    da.address = (description[-1].replace(",", ", ") + " WA").replace("  ", " ")
    if session.is_modified(da):
        da.date_scraped = today
        session.merge(da)
session.commit()
