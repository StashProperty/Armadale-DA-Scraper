import datetime
import sqlalchemy
from bs4 import BeautifulSoup
import requests
from sqlalchemy import Column, Integer, String, DATETIME
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
    date_created = Column(DATETIME, server_default=sqlalchemy.func.now())
    date_scraped = Column(DATETIME)


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

    da = DA(
        council_reference=slug,
        description=" - ".join(description),
        address=(description[-1].replace(",", ", ") + " WA").replace("  ", " "),
        date_scraped=today
    )
    session.merge(da)
session.commit()
