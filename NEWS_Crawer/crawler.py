import os
from NEWS_Crawer.__init__ import *
import subprocess
import re
import string
import requests
import datetime
from NEWS_Crawer.db import DB

from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
from dateutil.relativedelta import relativedelta



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
        				:param content: string
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
        ### gets the date of the publication and returns datetime object
        date_list = pub.find('span', class_='entry-date').getText().split()
        today = datetime.date.today()
        year=pub.find('span', class_='date-year')
        if not year:
            date_list.append(str(today.year))
        date_string = '/'.join(date_list)
        news_date = datetime.datetime.strptime(date_string, '%d/%b/%Y').date()
        return news_date
    def get_html(self,url)->string:
        ### creates request object from the url and returns HTML text
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
        ### creates beautifulsoup object from url and parses the html to find all news.
        page_links=[]
        if self.current_page!=0:
            page_url=self.url+'/'+str(self.current_page)
        else:
            page_url=self.url
        html=self.get_html(page_url)
        soup=bs(html,'html.parser')
        news=soup.find_all('article',class_='entry')
        for pub in news:
            ### selects the news not later than 10 days and appends page_links
            today=datetime.date.today()
            news_date=self.get_date(pub)
            diff=relativedelta(today,news_date)
            if diff.days<2:
                href=pub.find('a').get('href')
                if href:
                    full_url=urljoin(BASE_URL,href)
                    page_links.append(full_url)
        if page_links:
            ### updates self.seeds with the last current page links.
            self.seeds=[*self.seeds,*page_links]
            self.current_page+=1
            self.get_links()

    def get_pubs_data(self,link_url)->dict:
        ### receives the link_url from the seeds
        ### creates beautifulsoup object and parses to find the publication information
        ### returns dictionary

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
        ### gets the publication data and inserts the data to self.db() object
        pub_data=self.get_pubs_data(url)
        self.db.insert_row(pub_data)
    def run(self):
        ### deletes the old database news_table
        ### creates self.seeds list with urls
        ### saves the information to the newt_table

        self.db.delete_data_news_table()
        self.get_links()
        for link in self.seeds:
            self.save_pubs_data(link)
        print('Crawler finished its job!')

if __name__=='__main__':
    cr=Crawler(BASE_URL)
    cr.run()
    # print(cr.db.select_all_data())