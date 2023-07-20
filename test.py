import pandas as pd
import requests
from bs4 import BeautifulSoup


pagenumber = -1
url = f'https://www.wowprogress.com/pve/rating/next/{pagenumber}/?lang=de'
print(url)
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
soup

url = f'https://www.wowprogress.com/'


table = soup.find('table', {'class': 'rating'})
table
spans = soup.find_all('span')



###########################################
url = f'https://www.wowhead.com/item={item["id"]}/{currentItemName}?ilvl={item["ilvl"]}'
print(url)
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
spans = soup.find_all('span')

# Only use first value found
intOpen = True
critOpen = True
versOpen = True
masteryOpen = True
hasteOpen = True

# Get stat values
for span in spans:
    if "Intellect" in str(span) and intOpen:
        intSplit = str(span).split('+',1)[1].split('<',1)[0].split(' ',1)
        itemData.at[index, 'Int'] = intSplit[0].replace(",","")
        intOpen = False

    if "Critical Strike" in str(span) and critOpen:
        critSplit = str(span).split('>',2)[2].split(' ',1)
        itemData.at[index, 'Crit'] = str(critSplit[0])
        critOpen = False

    if "Mastery" in str(span) and masteryOpen:
        masterySplit = str(span).split('>',2)[2].split(' ',1)
        itemData.at[index, 'Mastery'] = str(masterySplit[0])
        masteryOpen = False

    if "Haste" in str(span) and hasteOpen:
        hasteSplit = str(span).split('>',2)[2].split(' ',1)
        itemData.at[index, 'Haste'] = str(hasteSplit[0])
        hasteOpen = False

    if "Versatility" in str(span) and versOpen:
        versSplit = str(span).split('>',2)[2].split(' ',1)
        itemData.at[index, 'Vers'] = str(versSplit[0])
        versOpen = False