import requests
import mysql.connector
from mysql.connector import Error
import datetime
import time

url = 'http://cf69fa90f2c9.ngrok.io/'

class ConnectDB():
    def __init__(self, host, database, user, password):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = self.connect()

    def connect(self):
        try:
            connection = mysql.connector.connect(host=self.host,
                                         database=self.database,
                                         user=self.user,
                                         password=self.password)
        except Error as e:
            print("Error reading data from MySQL table", e)
        
        return connection

    def get_data_from_table(self, sql_query):
        # connection = self.connect()
        # sql_select_Query_post = "select title from posts"
        results = []
        if (self.connection.is_connected()):
            cursor = self.connection.cursor()
            cursor.execute(sql_query)
            records = cursor.fetchall()
            # print("Total number of rows in posts is: ", cursor.rowcount)

            for row in records:
                results.append(row[0])
            cursor.close()
        else:
            print("MySQL is not connection")
        return results

    def conn_close(self):
        if  self.connection.is_connected():
            self.connection.close()
            print("MySQL connection is closed")

    def insert_into_suggestion(self, test1, test2):
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        if (self.connection.is_connected()):
            cursor = self.connection.cursor()
            try:
                cursor.execute("""INSERT into suggestion (suggest_id,post_id,created_at,updated_at) values(%s,%s,%s,%s)""",(test1, test2, timestamp, timestamp))
                self.connection.commit()
            except Exception as e:
                print(e)
                self.connection.rollback()
        else:
            print("MySQL is not connection")

    def delete_info_suggestion(self, post_id):
        if (self.connection.is_connected()):
            cursor = self.connection.cursor()
            try:
                sql_Delete_query = """Delete from suggestion WHERE suggest_id=%s;"""%(post_id)
                print(sql_Delete_query)
                cursor.execute(sql_Delete_query)
                self.connection.commit()
            except Exception as e:
                print(e)
        else:
            print("MySQL is not connection")

def queryDB(post_id):
    start = time.time()

    dataBase = ConnectDB('localhost', 'medium1', 'medium1', 'scret123')
    sent = dataBase.get_data_from_table("select title from posts")

    end = time.time()
    print("Total time connect DB: ", end-start)

    query_sent = sent[post_id-1]
    myobj = {'query': query_sent,
             'data': sent}

    resp = requests.post(url, json=myobj)
    sentenc = resp.json()["result"]
    print("Total time connect DB: ", time.time()-end)

    list_sg = []
    try:
        for i in range(len(sentenc)):
            if i == 0:
                continue
            sql_query_i = """select id from posts where title='%s';"""%(sentenc[i])
            id_ = dataBase.get_data_from_table(sql_query_i)
            list_sg.append(id_[0])
    except Exception as e:
        print(e)

    dataBase.delete_info_suggestion(post_id)
    for i in list_sg:
        dataBase.insert_into_suggestion(post_id, i)

    print(resp.json()["statusCode"])
    print("Total time query: ", time.time()-start)
    dataBase.conn_close()


import sys
arg = sys.argv

if __name__ == "__main__":
    post_id = int(arg[1])
    
    queryDB(post_id)
