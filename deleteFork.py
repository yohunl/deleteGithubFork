#!/usr/bin/env python3
import sys
import requests
from bs4 import BeautifulSoup

loginName = sys.argv[1]
longinPwd = sys.argv[2]

print("loginname" + loginName)
print("longinPwd" + longinPwd)

Base_URL = "https://github.com/login"
Login_URL = "https://github.com/session"

def get_github_html(url):
    '''
    这里用于获取登录页的html，以及cookie
    :param url: https://github.com/login
    :return: 登录页面的HTML,以及第一次的cooke
    '''
    response = requests.get(url)
    first_cookie = response.cookies.get_dict()
    return response.text, first_cookie



def get_token(html):
    '''
    处理登录后页面的html
    :param html:
    :return: 获取csrftoken
    '''
    soup = BeautifulSoup(html,'lxml')
    res = soup.find("input",attrs={"name":"authenticity_token"})
    token = res["value"]
    return token


def gihub_login(url,token,cookie):

    '''
    这个是用于登录
    :param url: https://github.com/session
    :param token: csrftoken
    :param cookie: 第一次登录时候的cookie
    :return: 返回第一次和第二次合并后的cooke
    '''

    data = {
        "commit": "Sign in",
        "utf8": "✓",
        "authenticity_token": token,
        "login": loginName,
        "password": longinPwd
    }

    response = requests.post(url, data=data, cookies=cookie)
    print(response.status_code)
    cookie = response.cookies.get_dict()
    return cookie

def get_list(cookie):
    items = []
    ret = requests.get("https://github.com/settings/repositories", cookies=cookie)
    html = ret.text
    cookie2 = ret.cookies.get_dict()
    cookie.update(cookie2)
    #编写爬虫时候,最常用的就是BeautifulSoup和lxml两个库,现在的BeautifulSoup也可以基于lxml来解析了,使用BeautifulSoup(html, 'lxml')
    soup = BeautifulSoup(html, 'lxml')
    res = soup.find_all("div", attrs={"class": "listgroup-item simple public fork js-collab-repo"})
    for i in res:
        item = i.find('a', attrs={'class': 'mr-1'}).string
        items.append(item)
    return items, cookie


def delete_rep(items,cookie):
    for item in items:
        setting_url ='https://github.com/' + item + '/settings'
        delete_url = setting_url + '/delete'
        set_ret = requests.get(url=setting_url, cookies=cookie).text
        # print(set_ret)
        soup = BeautifulSoup(set_ret, 'lxml')
        actionurl = '/' + item + '/settings' + '/delete'
        res = soup.find_all("form", attrs={"class": "js-normalize-submit"})
        length = len(res)
        if length <= 0:
            continue
        if item == "yohunl/ghost-theme-kaldorei":
        	continue
        token = res[1].find('input', attrs={'name': 'authenticity_token'})
        token = token["value"]
        # print(token)
        
        data = {
            'utf8': '✓',
            '_method': 'delete',
            'authenticity_token': token,
            'verify': item,
            'sudo_password': longinPwd,
            'user_id':loginName,
            'sudo_referrer':setting_url
        }
        ret_code = requests.post(delete_url, cookies=cookie, data=data).status_code
        print(ret_code)
        if ret_code != 200:
            print(item + ' not delete..')
        else:
            print('delete {_it} success...'.format(_it=item))

if __name__ == '__main__':
    html, cookie = get_github_html(Base_URL)
    token = get_token(html)
    cookie = gihub_login(Login_URL, token, cookie)
    items, cookie = get_list(cookie)
    delete_rep(items, cookie)

