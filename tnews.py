from datetime import datetime
from pampy import match
import re
from requests_html import HTMLSession
session = HTMLSession()
import telegram

def get_media_list():
    r = session.get('https://m.news.naver.com/newspaper/home.nhn')
    return [{'id': li.attrs['id'], 'title': li.find('img', first=True).attrs['alt']} for li in r.html.find('ul.offc_lst._headline_list > li')]

media_dict = {media['id']: media for media in get_media_list()}

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
        return [summary for summary in rj['summary'].split('<br/>') if summary]
    return None

def get_content(article_link):
  r = session.get(article_link)
  return r.html.find('div#newsct_article')[0]

def get_telegram_message(title, day, index, article):
    message = [f"[{title}({day})-{index}]({article['link']})"]
    for summary in get_summary(article['link']):
        message.append(f"- {summary}")
    return '\n'.join(message)


def send_telegram(media, day):
    chat_token = "5349929547:AAHd2FSvbKsVNFdN-fK8uXtzqVts9jYrodU"
    chat_id = '738042920'
    chat = telegram.Bot(token = chat_token)
    for i, article in enumerate(get_article_list(media, day)):
        message = get_telegram_message(media_dict[media]['title'], day, i, article)
        chat.sendMessage(chat_id, parse_mode='Markdown', text=message)


day = datetime.now().strftime('%Y%m%d')
print(day)

# {'009': {'id': '009', 'title': '매일경제'},
#  '015': {'id': '015', 'title': '한국경제'},
#  '011': {'id': '011', 'title': '서울경제'},
#  '353': {'id': '353', 'title': '중앙SUNDAY'},
#  '088': {'id': '088', 'title': '매일신문'},
#  '020': {'id': '020', 'title': '동아일보'},
#  '028': {'id': '028', 'title': '한겨레'},
#  '005': {'id': '005', 'title': '국민일보'},
#  '032': {'id': '032', 'title': '경향신문'},
#  '022': {'id': '022', 'title': '세계일보'},
#  '023': {'id': '023', 'title': '조선일보'},
#  '469': {'id': '469', 'title': '한국일보'},
#  '021': {'id': '021', 'title': '문화일보'},
#  '082': {'id': '082', 'title': '부산일보'},
#  '016': {'id': '016', 'title': '헤럴드경제'},
#  '029': {'id': '029', 'title': '디지털타임스'},
#  '014': {'id': '014', 'title': '파이낸셜뉴스'},
#  '008': {'id': '008', 'title': '머니투데이'},
#  '081': {'id': '081', 'title': '서울신문'},
#  '030': {'id': '030', 'title': '전자신문'},
#  '640': {'id': '640', 'title': '코리아중앙데일리'},
#  '087': {'id': '087', 'title': '강원일보'},
#  '277': {'id': '277', 'title': '아시아경제'},
#  '044': {'id': '044', 'title': '코리아헤럴드'},
#  '018': {'id': '018', 'title': '이데일리'}}

send_telegram('029', day)
send_telegram('030', day)
