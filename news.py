import pandas as pd
from gspread_pandas import Spread, Client
from pampy import match
import re
from requests_html import HTMLSession
session = HTMLSession()

def get_media_list():
    r = session.get('https://m.news.naver.com/newspaper/home.nhn')
    return [{'id': li.attrs['id'], 'title': li.find('img', first=True).attrs['alt']} for li in r.html.find('ul.offc_lst._headline_list > li')]

def get_article_list(media, ymd):
    url = 'https://media.naver.com/press/{}/newspaper?date={}'
    r = session.get(url.format(media, ymd))
    article_list = [{'title': article.find('strong', first=True).text, 'link': article.find('a', first=True).attrs['href']} for article in r.html.find('ul.newspaper_article_lst > li')]
    return article_list

def get_summary(article_link):
    m = match(article_link, re.compile('https://.+/.+/.+/([0-9]+)/([0-9]+)'), lambda m, a: (m, a))
    r = session.get('https://tts.news.naver.com/article/{}/{}/summary'.format(*m))
    rj = r.json()
    if 'summary' in rj:
        return rj['summary']
    return None


article_list = get_article_list('028', '20190504')
for article in article_list:
    article['summary'] = get_summary(article['link'])

df = pd.DataFrame(article_list)

# file_name = "http://stats.idre.ucla.edu/stat/data/binary.csv"
# df = pd.read_csv(file_name)

# 'Example Spreadsheet' needs to already exist and your user must have access to it
spread = Spread('moondatatrader', '20190504', create_spread=True)
# This will ask to authenticate if you haven't done so before for 'example_user'

# Display available worksheets
# spread.sheets

# Save DataFrame to worksheet 'New Test Sheet', create it first if it doesn't exist
spread.df_to_sheet(df, index=False, sheet='한겨레', start='A1', replace=True)
print(spread)
# <gspread_pandas.client.Spread - User: '<example_user>@gmail.com', Spread: 'Example Spreadsheet', Sheet: 'New Test Sheet'>

# You can now first instanciate a Client separately and query folders and
# instanciate other Spread objects by passing in the Client
# client = Client('moondatatrader')
# # Assumming you have a dir called 'example dir' with sheets in it
# available_sheets = client.find_spreadsheet_files_in_folders('example dir')
# spreads = []
# for sheet in available_sheets.get('example dir', []):
#     spreads.append(Spread(client, sheet['id']))