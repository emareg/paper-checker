import requests
import urllib
import re
from bs4 import BeautifulSoup

headers_Get = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'de-DE,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }


def search( searchstr, num=10 ):
    q = urllib.parse.quote_plus(searchstr)
    # todo: improve query: %2Bterm?


    #print("Requesting: ", q)
    s = requests.Session()
    url = 'https://www.google.com/search?q=' + q + '&ie=utf-8&oe=utf-8'    # &num={}'.format(num)
    html_res = s.get(url, headers=headers_Get).text


    RES_START='>Webergebnisse</h2>'             # '<div id="search">'
    RES_END='<div id="foot'
    ENTRY_DEL='<div class="g">'
    html_res = html_res[html_res.index(RES_START)+len(RES_START):html_res.index(RES_END)]

    output=[]

    results = re.findall( r'<div class="g">(.*?)(?=><div class="g">)', html_res, re.DOTALL)
    for result in results:
        #print("Result:", result)
        title = re.findall( r'<h3 class=.*?>(.*?)</h3>', result, re.DOTALL)[0]
        url = re.findall( r'<div class="r">.*?<a href="(.*?)"', result, re.DOTALL)[0]
        desc = re.findall( r'<span class="st">(?:<span class="f">.*?</span>)?(.*?)</span>', result, re.DOTALL)[0]
        output.append({'title': title, 'url': url, 'desc': desc})

    return output

