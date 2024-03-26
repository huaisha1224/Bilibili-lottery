#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import random
import requests
import json

def Get_Aid_From_BVid(BVid):
    """
    将哔哩哔哩视频的BVid转为Aid号。
    如果输入的是纯数字字符串，则认为已经是Aid号并直接返回。
    参数：
    BVID -- 输入的BVid字符串
    返回：
    int类型 -- 转换后的Aid号
    https://api.bilibili.com/x/web-interface/view?bvid=BV1DA4m1P7ZS
    """
    # 检查BVid是否可以转换为整数且非空字符串,判断用户输入的是BVid还是Aid
    if BVid.isdigit() and BVid != '':
        return int(BVid)
    # 如果是BVid就通过api接口查询视频信息，并获取到Aid
    else:
        url = f'https://api.bilibili.com/x/web-interface/view?bvid={BVid}'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0'}
        response = requests.get(url,headers=headers)
        data = response.text
        aid = re.findall(r'"aid":(\d+),', data)
        # print(f'Aid：{aid[0]}')
        return aid[0]


def fetch_and_analyze_comments(BVID):
    """
    根据BVID获取并分析哔哩哔哩视频的所有评论信息。

    参数:
    BVID (str): B站视频的BVid

    返回:
    tuple: 包含去重后的用户名列表（set类型）和总评论数（int类型）
    """
    
    # 设置请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
    }

    # 初始化变量
    pagenum = 1
    commentnum = 0
    commentlist = []  # 存储清洗后的评论字典列表
    all_usernames = []  # 存储所有评论用户的用户名列表

    # 循环遍历评论页
    while True:
        # 获取当前BVid对应的Aid
        oid = Get_Aid_From_BVid(BVID)

        # 构造分页请求URL
        url = f"https://api.bilibili.com/x/v2/reply?pn={pagenum}&type=1&oid={oid}&sort=2"
        
        # 发送请求并处理响应
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        comment = json.loads(response.text)

        # 处理非0或-412的错误代码
        if comment['code'] not in [0, -412]:
            print(f'抓取失败，错误代码：{comment["code"]}')
            exit(0)

        # 处理访问频率过高错误
        if comment['code'] == -412:
            print('抓取失败，访问频率过高！错误代码：-412，请稍后再试！')
            exit(0)

        # 获取当前页的评论
        comments = comment['data']['replies']
        if not comments:  # 如果当前页没有评论，则结束循环
            break

        # 遍历当前页的评论并提取用户信息
        for index in range(len(comments)):
            uname = comments[index]['member']['uname']
            mid = comments[index]['mid']
            avatar = comments[index]['member']['avatar']
            like = comments[index]['like']
            content = comments[index]['content']['message']

            # 存储评论信息
            userdict = {
                '用户名': uname,
                'UID': mid,
                '头像': avatar,
                '点赞数': like,
                '评论': content
            }
            commentlist.append(userdict)
            all_usernames.append(uname)

        # 更新页码数和总评论数
        pagenum += 1
        commentnum += len(comments)

    # 输出抓取结果
    print(f'共计抓取到 {commentnum} 条评论')
    print(f'共有 {len(set(all_usernames))} 个不同用户')

    # 返回去重后的用户名列表和总评论数
    unique_usernames = set(all_usernames)
    draw_winners(unique_usernames, 3)
    return unique_usernames, commentnum

def draw_winners(unique_usernames, number_of_winners):
    """
    随机从去重之后的用户列表中抽取中奖用户，实现抽奖功能。

    参数:
    - unique_usernames (list): 一个已经去重处理过的用户名列表，每个元素代表一个唯一的用户。
    - number_of_winners (int): 指定要抽取的中奖用户数量。

    返回值:
    - winners (list): 包含中奖用户名的列表，其长度不超过 `number_of_winners` 并且不会大于 `unique_usernames` 的总长度。
    """
    unique_usernames_list = list(unique_usernames)
    winners = random.sample(unique_usernames_list, min(number_of_winners, len(unique_usernames)))
    print(f'中奖用户:{winners}')
    return winners
    
if __name__ == '__main__':
    fetch_and_analyze_comments('BV1DA4m1P7ZS')
