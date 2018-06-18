from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re
import time
import pymysql
import pymysql.cursors

connection = pymysql.connect(host='localhost',
                             user='root',
                             password='',
                             db='twitterscraper',
                             charset='utf8')

def collectdata():

    link = (input("Enter the MEMBERS PAGE of the FB group URL: "))
    numtoscrape = int(input("Enter the number of posts you want to scrape: "))
    databasename = (input("Enter databasename name: "))
    create_database(databasename)

    driver = webdriver.Chrome(executable_path="/Users/clickontemp/Downloads/chromedriver")
    driver.get(link)

    postsscraped = 0

    while postsscraped < numtoscrape:

        source = driver.page_source
        soup = BeautifulSoup(source, "html.parser")

        post_containers = soup.findAll("div",{"id":"timeline"})[0]
        listof = post_containers.findAll("li",{"class":"js-stream-item stream-item stream-item "})
        postsloaded = len(listof)
        for post in listof[postsscraped:]:
            postid = postsscraped + 1
            date_title = post.findAll("small",{"class":"time"})[0].a["title"]
            date_time = tweettime(date_title)
            url = 'https://twitter.com' + post.findAll("small",{"class":"time"})[0].a["href"]
            handle = post.findAll("span",{"class":"username u-dir u-textTruncate"})[0].b.text
            text = post.findAll("div",{"class":"js-tweet-text-container"})[0].p.text
            likestring = post.findAll("span",{"class":"ProfileTweet-action--favorite u-hiddenVisually"})[0].findAll("span",{"class":"ProfileTweet-actionCountForAria"})[0].text
            likes = int(re.sub("[^0-9]", "", likestring))
            replystring = post.findAll("span",{"class":"ProfileTweet-action--reply u-hiddenVisually"})[0].findAll("span",{"class":"ProfileTweet-actionCountForAria"})[0].text
            replies = int(re.sub("[^0-9]", "", replystring))
            retweetstring = post.findAll("span",{"class":"ProfileTweet-action--retweet u-hiddenVisually"})[0].findAll("span",{"class":"ProfileTweet-actionCountForAria"})[0].text
            retweets = int(re.sub("[^0-9]", "", retweetstring))

            writedata(databasename, postid, date_time, url, handle, likes, replies, retweets)
            postsscraped+=1

            print(postsscraped)
            print(date_title)
            print(url)
            print(handle)
            print(likestring)
            print(replystring)
            print(retweetstring)
            if postsscraped == numtoscrape:
                break

        for i in range(100):
            driver.execute_script("window.scrollTo(0, 11111080)")
            time.sleep(0.1)
        time.sleep(2)
    driver.close()


def tweettime(timestring):
    timestringsplit = timestring.split(' ')
    minute = timestringsplit[0].split(':')[1]
    second = '00'
    year = timestringsplit[5]
    monthstring = timestringsplit[4]

    if len(timestringsplit[3]) == 1:
        day = '0' + timestringsplit[3]
    elif len(timestringsplit[3]) == 2:
        day = timestringsplit[3]
    if timestringsplit[1] == 'am':
        if len(timestringsplit[0].split(':')[0]) == 1:
            hour = '0' + timestringsplit[0].split(':')[0]
        elif len(timestringsplit[0].split(':')[0]) == 2:
            hour = timestringsplit[0].split(':')[0]
    elif timestringsplit[1] == 'pm':
        hour = str(int(timestringsplit[0].split(':')[0]) + 12)
    if monthstring == 'Jan':
        month = '01'
    elif monthstring == 'Feb':
        month = '02'
    elif monthstring == 'Mar':
        month = '03'
    elif monthstring == 'Apr':
        month = '04'
    elif monthstring == 'May':
        month = '05'
    elif monthstring == 'Jun':
        month = '06'
    elif monthstring == 'Jul':
        month = '07'
    elif monthstring == 'Aug':
        month = '08'
    elif monthstring == 'Sep':
        month = '09'
    elif monthstring == 'Oct':
        month = '10'
    elif monthstring == 'Nov':
        month = '11'
    elif monthstring == 'Dec':
        month = '12'

    return year + '-' + month + '-' + day + ' ' + hour + ':' + minute + ':00.000'


def create_database(tblName):

    cur = connection.cursor()

    try:
        #Create a table in mysql???
        createsql = "CREATE TABLE %s ( \
          `post_id` int(11) DEFAULT NULL, \
          `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, \
          `date_time` varchar(255) DEFAULT NULL, \
          `url` varchar(255) DEFAULT NULL, \
          `twitterhandle` varchar(255) DEFAULT NULL, \
          `likes` int(11) DEFAULT NULL, \
          `replies` int(11) DEFAULT NULL, \
          `retweets` int(11) DEFAULT NULL \
        )" % (tblName)

        cur.execute(createsql)

    except pymysql.err.InternalError as e:
        code, msg = e.args
        if code == 1050:
            print(tblName, 'already exists')

def writedata(tablename, postid, date_time, url, handle, likes, replies, retweets):
    cur = connection.cursor()
    sql = "INSERT INTO %s(post_id, date_time, url, twitterhandle,likes, replies, retweets) \
   VALUES ('%d', '%s', '%s', '%s','%d', '%d', '%d')" % (tablename, postid, date_time, url, handle,likes, replies, retweets)
  

    cur.execute(sql)

    connection.commit()

collectdata()



