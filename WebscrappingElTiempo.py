import sqlite3
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import ssl
import csv, xlsxwriter
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

conn = sqlite3.connect('news.db')
cur = conn.cursor()
email_user = 'EMAIL'
email_password = 'PASSWORD'
email_send = 'EMAIL SENDER'
subject = 'subject'

msg = MIMEMultipart()
msg['From'] = email_user
msg['To'] = email_send
msg['Subject'] = subject

cur.executescript('''
DROP TABLE IF EXISTS Tiempo;
CREATE TABLE Tiempo (
    titulo TEXT,
    Noticia TEXT
);
''')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://www.eltiempo.com/"
html = urllib.request.urlopen(url, context=ctx).read()
sopa = BeautifulSoup(html, 'html.parser')

lst = list()
# Recuperar todas las etiquetas de anclaje
for article in sopa.find_all("h3", class_="listing-title box-title"):
    ##headline = article.h3.a
    ##print(headline.text)
    headline = (article.text)
    lst.append(headline)
for item in lst:
   print(item)
lst2 = list()
for i in sopa.find_all("h3", class_="listing-title box-title"):
    ##headline = article.h3.a
    ##print(headline.text)
   link = i.find('a',href=True)
   respuesta= str(link['href'])
   lst2.append(respuesta)
lst3 = list()
for link in lst2:
    url = "https://www.eltiempo.com/"+link
    html = urllib.request.urlopen(url, context=ctx).read()
    sopa = BeautifulSoup(html, 'html.parser')

    article = sopa.find("div", class_="articulo-contenido")
    if article is None:
        continue
    #print(article.text)
    lst3.append(article.text)

lst4 = list()
for noticia in range(6):
    #print(lst[noticia] + lst3[noticia].split('\n')[4])
    lst4.append((str(noticia + 1)+'.'+'Noticia') + lst[noticia] + lst3[noticia].split('\n')[4])
    x = "\n\n".join(lst4)

    cur.execute('''INSERT INTO Tiempo (titulo ,Noticia)
                VALUES (?,?)''', (lst[noticia],lst3[noticia].split('\n')[4],))

    conn.commit()
cur.close()

body = x
msg.attach(MIMEText(body,'plain'))

text = msg.as_string()
server = smtplib.SMTP('smtp.gmail.com',587)
server.starttls()
server.login(email_user,email_password)


server.sendmail(email_user,email_send,text)
server.quit()
