import pandas as pd
from gspread_pandas import Spread, Client
from pampy import match
import re
from requests_html import HTMLSession
from datetime import datetime
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


media_list = [{'id': '028', 'title': '한겨레'},
 {'id': '022', 'title': '세계일보'},
 {'id': '023', 'title': '조선일보'},
 {'id': '044', 'title': '코리아헤럴드'},
 {'id': '081', 'title': '서울신문'},
 {'id': '015', 'title': '한국경제'},
 {'id': '025', 'title': '중앙일보'},
 {'id': '030', 'title': '전자신문'},
 {'id': '032', 'title': '경향신문'},
 {'id': '008', 'title': '머니투데이'},
 {'id': '018', 'title': '이데일리'},
 {'id': '014', 'title': '파이낸셜뉴스'},
 {'id': '009', 'title': '매일경제'},
 {'id': '029', 'title': '디지털타임스'},
 {'id': '020', 'title': '동아일보'},
 {'id': '011', 'title': '서울경제'},
 {'id': '469', 'title': '한국일보'},
 {'id': '005', 'title': '국민일보'},
 {'id': '021', 'title': '문화일보'},
 {'id': '277', 'title': '아시아경제'},
 {'id': '016', 'title': '헤럴드경제'}]


if __name__ == '__main__':
    ymd = datetime.now().strftime('%Y%m%d')
    for media in media_list:
        article_list = get_article_list(media['id'], ymd)
        for article in article_list:
            article['summary'] = get_summary(article['link'])

        df = pd.DataFrame(article_list)

        spread = Spread('moondatatrader', 'newspaper', create_spread=True)
        spread.df_to_sheet(df, index=False, sheet=media['title'], start='A1', replace=True)