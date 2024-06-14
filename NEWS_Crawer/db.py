import mysql.connector as mc
# from __init__ import *
from configparser import ConfigParser
import os
from datetime import date


class DB():
    def __init__(self):
        try:
            mysql_config = self.config_parse('config.ini', 'mysql')
            db1=mc.connect(host=mysql_config["host"],user=mysql_config["user"],
                           passwd=mysql_config["password"],port=mysql_config["port"])
            with db1.cursor() as cursor:
                sql = "CREATE DATABASE IF NOT EXISTS faktor_bg_news"
                cursor.execute(sql)
            self.conn=mc.connect(**mysql_config)
            # self.drop_news_table()
            self.create_news_table()
        except mc.Error as e:
            print(e)
    def config_parse(self,filename,section):
        config_db= {}
        parser=ConfigParser()
        package_directory = os.path.dirname(os.path.abspath(__file__))
        if parser.read(os.path.join(package_directory,filename)):
            if parser.has_section(section):
                items=parser.items(section)
                for item in items:
                    config_db[item[0]]=item[1]
            else:
                raise Exception(f'{section} not found in the {filename} file')
        else:
            raise Exception(f'{filename} file not found')
        return config_db

    def create_news_table(self):
        sql = """
    			CREATE TABLE IF NOT EXISTS news_table(
    				id INT AUTO_INCREMENT PRIMARY KEY,
    				title VARCHAR(100) NOT NULL,
    				pub_date DATE NOT NULL,
    				content TEXT,
    				created_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    				updated_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    				CONSTRAINT title_date UNIQUE (title, pub_date)
    			);
    		"""
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            self.conn.commit()

    def insert_row(self, row_data):
        sql = """
    			INSERT IGNORE INTO news_table
    				(title, pub_date, content)
    				VALUES ( %s, %s, %s)
    		"""

        with self.conn.cursor(prepared=True) as cursor:
            cursor.execute(sql, tuple(row_data.values()))
            self.conn.commit()
    def insert_rows(self,rows_data):
        sql="""
            INSERT IGNORE INTO news_table
			(title, pub_date, content)
			VALUES ( %s, %s, %s)
			"""

        with self.conn.cursor(prepared=True) as cursor:
            cursor.executemany(sql, rows_data)
            self.conn.commit()

    def get_last_updated_date(self):
        sql = 'SELECT MAX(updated_at) AS "Max Date" FROM news_table;'
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchone()

        if result:
            return result[0]
        else:
            raise ValueError('No data in table')
    def select_all_data(self):
        sql="SELECT * FROM news_table"
        with self.conn.cursor(buffered=True) as cursor:
            cursor.execute(sql)
            result=cursor.fetchall()
        return result

    def get_column_names(self):
        # sql = "SELECT id, title, pub_date, content FROM  news_table LIMIT 1;"
        # sql="SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = 'news_table';"
        sql="""SELECT DISTINCT COLUMN_NAME FROM
        INFORMATION_SCHEMA.COLUMNS
        WHERE COLUMN_NAME  IN ('id', 'title','pub_date','content','created_at','updated_at')
        AND TABLE_NAME = 'news_table';"""
        with self.conn.cursor(buffered=True) as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
        result_list=list(item[0] for item in result)
        return result_list
    def delete_data_news_table(self):
        sql = "TRUNCATE TABLE news_table;"

        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            self.conn.commit()

if __name__=='__main__':
    db=DB()
#     row_data_= dict(tltle='news1', pub_date=date(2023,12,23), content='text1')
#     # row_data_=['news1',date(2023,12,23),'text1']
#     rows_data=[
#         ('news2',date(2023,12,24),'text2'),
#         ('news3',date(2023,12,25),'text3'),
#         ('news4',date(2023,12,26),'text4')
#     ]

    # db.create_news_table()
    # db.insert_row(row_data_)
    # db.insert_rows(rows_data)
    # db.reset_indexes_table()
    # print(db.select_all_data())
    # print(db.get_column_names())
    # db.get_last_updated_date()
    # db.delete_data_news_table()
