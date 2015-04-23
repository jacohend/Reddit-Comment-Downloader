#Author: Meditato
#File: User_Comments.py
#Date: 14 June 2012

import json
import urllib.request
import time
import html.parser
import cgi
import codecs
import unicodedata

user = 'meditato'

#Find "Meditato" below and change it to your username!

def decode(bytes):      #decode characters into ASCII string
    try:
        text = bytes.decode('utf-8')
    except UnicodeDecodeError:
        try:
            text = bytes.decode('iso-8859-1')
        except UnicodeDecodeError:
            text = bytes.decode('cp1252')
    return text

def encode(bytes):      #encode characters into UTF if possible. We do a decode(encode(text)) to get translate weird escaped characters, such as in the Face of Disapproval
    try:
        text = bytes.encode('utf-8')
    except UnicodeEncodeError:
        try:
            text = bytes.encode('iso-8859-1')
        except UnicodeEncodeError:
            text = bytes.encode('cp1252')
    return text

def retrieveJSON(url):  #This identifies the User-Agent (required by Reddit) and then downloads/decodes the JSON url
        time.sleep(3)   #we have to wait between requests so we don't piss off Reddit
        print('Fetching from link ' + url + '\n')
        req = urllib.request.build_opener()
        req.addheaders = [('User-agent', 'Comment grabber by /u/Meditato')]
        req = req.open(url)
        encoding = req.headers.get_content_charset()
        data = req.readall().decode(encoding)
        return json.loads(data)

def commentQuotes(str): #make blockquotes a bit more "reddity". I could do this more efficiently but I don't know Python
        index = str.find('<blockquote>')
        if index != -1:
                tail = str[(index + 16):]
                str = str[:(index + 16)] + '| ' + commentQuotes(tail)
        return str

url = 'http://www.reddit.com/user/' + user + '.json?limit=500'
data = retrieveJSON(url)

FILE = open(user + '\'s Comments.html','w') #create our file
FILE.write('<!DOCTYPE html><html><body></br>')  #make it html

while(1):
    for ob in data['data']['children']:
        obj = ob['data']
        if 'kind' in ob:        #we must be able to tell what type of post this is
            if ob['kind'] == 't1':      #this is a comment, treat accordingly
                link_id =(obj['link_id'].split('_'))[1]
                cid = obj['id']
                link_title = obj['link_title'].replace(' ', '_')
                subreddit = obj['subreddit']
                FILE.writelines(commentQuotes(html.parser.HTMLParser().unescape(html.parser.HTMLParser().unescape(decode(encode(obj['body_html']))))))   #grab the comment body, convert to html, and write to file
                FILE.write('<a href=\"http://reddit.com/r/' + subreddit + '/comments/' + link_id + '/' + link_title[0] + '/' + cid + '\">Link</a></br></br><hr/>')      #write link to file
            elif ob['kind'] == 't3':    #this is a link submission, treat accordingly
                permalink = obj['permalink']
                title = obj['subreddit']
                str = 'Submission to /r/' + title + ': <a href=\"http://www.reddit.com' + permalink + '\">Link</a></br></br><hr/>'  
                FILE.writelines(str)    #write link submission to file
    after = data['data']['after']
    if after == None:   #if there's nothing left, leave
        break
    else:       #retrieve next page of comments
        url = 'http://www.reddit.com/user/' + user + '.json?after=' + after + '&limit=500'
        data = retrieveJSON(url)
        continue
FILE.write('</body><html>')     #finalize file and close
FILE.close()
