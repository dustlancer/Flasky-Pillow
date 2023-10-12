
from fileinput import filename
import math
import sqlite3
import os
import time

from requests import ReadTimeout


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def getMenu(self):  #такими запросами можно брать всё что угоно из БД
        sql = '''SELECT * FROM mainmenu'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: 
                return res
        except:
            print("Ошибка чтения из БД")
        return []


    def addPost(self, title, text):
        try:
            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO posts VALUES(NULL, ?, ?, ?)", (title, text, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления статьи в БД "+ str(e))
            return False
        return True


    def getPosts(self):
        sql = '''SELECT * FROM POSTS'''
        try: 
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res:
                return res
        except:
            print("Ошибка чтения из БД")
        return []


    def getUsers(self):
        sql = '''SELECT * FROM users'''
        try: 
            self.__cur.execute(sql)
            res = self.__cur.fetchone()

            if res:
                return res
                
        except:
            print("Ошибка чтения из БД")
        return []


    def addUser(self, name, hpsw):
        try:
            self.__cur.execute(f"SELECT COUNT() as 'count' FROM users WHERE name LIKE '{name}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print('Пользователь с таким именем уже существует')
                return false

            self.__cur.execute("INSERT INTO users VALUES(NULL, ?, ?)", (name, hpsw))
            self.__db.commit()

        except sqlite3.Error as e:
            print("Ошибка добавления пользователя в БД: " + str(e))
            return False

        return True


    def getUser(self, user_id):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print('Пользователь не найден')
                return False
            return res

        except sqlite3.Error as e:
            print("Ошибка получения данных из БД: " + str(e))
        return False


    def getUserByName(self, name):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE name = '{name}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print('Пользователь не найден')
                return False
            return res

        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))

        return False 

    def getPost(self, postId):
        sql = f"SELECT title, text FROM posts WHERE id = {postId} LIMIT 1"
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД " + str(e))
        return (False, False)

    
    def addPicture(self, file_name, user_name, user_id):
        try:
            self.__cur.execute(f"SELECT COUNT() as 'count' FROM pictures WHERE file_name LIKE '{file_name}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                idx = file_name.index('.')
                file_name = file_name[:idx] + '1'+ file_name[idx:]
  

            self.__cur.execute("INSERT INTO pictures VALUES(NULL, ?, ?, ?)", (file_name, user_name, user_id))
            self.__db.commit()

        except sqlite3.Error as e:
            print("Ошибка добавления изображения в БД: " + str(e))
            return False

        return True, file_name


    def fetchPicsFromFolder(self):
        # print(os.getcwd())
        directory = "static/data"
        # os.chdir("static/data")
        dat = []
        for user in os.listdir(directory):
            f = os.path.join(directory, user)
            if os.path.isdir(f): 
                for pic in os.listdir(f):
                    if not pic.startswith('.'):
                        dat.append([user, pic])

            
        #print(dat)
        self.__cur.execute("DELETE FROM pictures")
        for pic in dat:
            try:
                # pic[0] – username
                # pic[1] – filename
                # insert vaklues for fule_name. user_name, user_id
                self.__cur.execute("INSERT INTO pictures VALUES(NULL, ?, ?, ?)", (pic[1], pic[0], self.getUserID(pic[0])))
                self.__db.commit()
                #print(pic[1] + " added to " + pic[0] + " folder")
            except sqlite3.Error as e:
                print("can't fetch galleries from foler " + user + ": " + str(e))


    def getUserID(self, name):
        try:
            self.__cur.execute(f"SELECT id FROM users WHERE name = '{name}'")
            raw_id = self.__cur.fetchone()
            if raw_id:
                return raw_id[0]
            else: return False
        except sqlite3.Error as e:
            print("Can't get user ID by name, error: " + str(e))

    
    def getGallery(self, user_name):
        sql = f"SELECT * FROM pictures WHERE user_name = '{user_name}'"
        try: 
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res:
                return res
            else: print('no result during getting gallery')
                
            
        except sqlite3.Error as e:
            print("Ошибка получения галереи пользователя из БД " + str(e))

