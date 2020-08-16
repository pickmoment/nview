import justpy as jp
from requests_html import HTMLSession
import datetime

media_list = {'015': '한국경제', '030': '전자신문', '009': '매일경제'}

session = HTMLSession()

@jp.SetRoute('/')
def index():
    wp = jp.WebPage()
    ymd = datetime.date.today().strftime("%Y%m%d")
    for media_id in media_list:
        d = jp.Div(a=wp, classes='flex bg-blue-200 text-lg p-2 m-2')
        jp.A(text=media_list[media_id], href=f'/news/{media_id}/{ymd}', a=d)
    return wp

@jp.SetRoute('/news/{media_id}/{ymd}')
async def news(request):
    media_id = request.path_params.get('media_id', '009')
    ymd = request.path_params.get('ymd', '20200101')

    wp = jp.WebPage()
    head = jp.Div(a=wp, classes='text-lg')
    jp.A(text='Home', href='/', a=head, classes='p-2 bg-green-200')
    jp.Span(text=media_list[media_id], a=head, classes='m-2 p-2 bg-blue-200')
    jp.A(text='<', href=f'/news/{media_id}/{get_next_ymd(ymd, -1)}', a=head, classes='p-2 bg-red-200')
    jp.Span(text=ymd, a=head, classes='p-2 bg-red-100')
    jp.A(text='>', href=f'/news/{media_id}/{get_next_ymd(ymd, 1)}', a=head, classes='p-2 bg-red-200')
    articles = get_article_list(media_id, ymd)

    for article in articles:
        div = jp.Div(a=wp, classes='flex bg-gray-200 p-1 m-1 text-lg')
        jp.A(text=article['title'], href=article['link'], a=div)

    return wp

def get_next_ymd(ymd, diff):
    day = datetime.datetime.strptime(ymd, '%Y%m%d')
    return (day + datetime.timedelta(diff)).strftime('%Y%m%d')

    

def get_article_list(media, ymd):
    url = f'https://media.naver.com/press/{media}/newspaper?date={ymd}'
    r = session.get(url)
    article_list = [{'title': article.find('strong', first=True).text, 'link': article.find('a', first=True).attrs['href']} for article in r.html.find('ul.newspaper_article_lst > li')]
    return article_list


jp.justpy()