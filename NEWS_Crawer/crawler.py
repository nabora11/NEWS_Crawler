import os
import re
import string
import requests
import datetime
from db import DB

from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
from dateutil.relativedelta import relativedelta
BASE_URL="https://faktor.bg/bg/articles/novini"

LINKS=[
'https://faktor.bg/bg/articles/novini-balgariya-bogoslov-ne-e-izklyucheno-mitropolit-nikolay-da-bade-nominiran-za-patriarh',
'https://faktor.bg/bg/articles/novini-balgariya-sotsialnata-komisiya-ne-odobri-zadalzhitelna-podkrepa-za-11-rast-na-pensiite',
'https://faktor.bg/bg/articles/novini-svyat-asandzh-poluchi-razreshenie-za-palno-obzhalvane-na-ekstradiraneto-si-v-sasht',
'https://faktor.bg/bg/articles/novini-balgariya-vtornikat-slanchev-sryadata-i-chetvartakat-obache-pak-shte-sa-dazhdovni',
'https://faktor.bg/bg/articles/novini-balgariya-glavchev-poiska-dans-da-proveri-prichinite-za-spirane-na-simeonovskiya-lift'
]

class Crawler():
    def __init__(self,url:string):
        self.url=url
        self.current_page=0
        self.seeds=[]
        self.status=0
        self.db=DB()

    def write_to_file(self,filename, content):
        """ Write string to given filename
        				:param filename: string
        				:param content: sring
        		"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
        except FileNotFoundError:
            print(f'File {filename} does not exists!')
        except Exception as e:
            print(f'Can not write to file: {filename}: {str(e)}')
            exit(-1)
    def get_date(self,pub:bs):
        date_list = pub.find('span', class_='entry-date').getText().split()
        today = datetime.date.today()
        year=pub.find('span', class_='date-year')
        if not year:
            date_list.append(str(today.year))
        date_string = '/'.join(date_list)
        news_date = datetime.datetime.strptime(date_string, '%d/%b/%Y').date()
        return news_date
    def get_html(self,url):
        try:
            r=requests.get(url)
        except requests.RequestException:
            r=requests.get(url,verify=False)
        except Exception as e:
            print(f'Can not get url:{url}!')
            exit(-1)
        r.encoding='utf-8'
        if r.ok:
            return r.text
        else:
            print('server can not return correct response Bye!')
            exit(-1)
    def get_links(self):
        page_links=[]
        if self.current_page!=0:
            page_url=self.url+'/'+str(self.current_page)
        else:
            page_url=self.url
        html=self.get_html(page_url)
        soup=bs(html,'html.parser')
        news=soup.find_all('article',class_='entry')
        for pub in news:
            today=datetime.date.today()
            news_date=self.get_date(pub)
            diff=relativedelta(today,news_date)
            if diff.days<5:
                href=pub.find('a').get('href')
                if href:
                    full_url=urljoin(BASE_URL,href)
                    page_links.append(full_url)
        if page_links:
            self.seeds=[*self.seeds,*page_links]
            self.current_page+=1
            self.get_links()

    def get_pubs_data(self,link_url):
        html=self.get_html(link_url)
        soup=bs(html,'html.parser')
        title=soup.find('h1',class_='text-center').getText()
        pub_date=self.get_date(soup)
        pub_content=soup.find('div',class_='entry-content').getText().strip()
        return {
            "title":title,
            "pub_date":pub_date.strftime('%Y-%m-%d'),
            "pub_content":pub_content
        }
    def save_pubs_data(self,url):
        pub_data=self.get_pubs_data(url)
        self.db.insert_row(pub_data)
    def run(self):
        # self.get_links()
        # for link in self.seeds:
        #     self.save_pubs_data(link)
        for link in LINKS:
            self.save_pubs_data(link)
        self.db.show_news_table()

if __name__=='__main__':
    cr=Crawler(BASE_URL)
    cr.run()