from pywebio.input import *
from pywebio import start_server
from pywebio.output import *
# from pywebio.session import set_env, info as session_info
import camelot.io as camelot
# import matplotlib.pyplot as plt
import pandas as pd
from pandas.core.frame import DataFrame
import tornado.ioloop
import os
import uuid
from tornado.web import StaticFileHandler
import numpy as np
import time


def main():
    # # 回主页标记
    # n = 0

    # 声明变量df
    global df

    # # 主程序
    # while True:
        # 放置小工具的标题
        # if n == 0:
        #     # put_image(open('d:/PyProjects/EY_projectplace/xks/downloads/wordLogo.png', 'rb').read())
        #     # put_image(open(r'd:/PyProjects/EY_projectplace/xks/downloads/EY_BigLogo.png', 'rb').read())
    put_image(open(r'/root/Project/SimpleBlog/downloads/combineLogo.jpg', 'rb').read())

        # # 输入文本
        # options = ['多行表格', '只有一行']
        # sel = radio(options=options, inline=False, required=True, help_text="⚠注意: 请根据您的表格的实际行数选择",
        #             label="请选择您要转换的PDF表格行数")
        # select('滴滴行程单中有几行数据 (默认多行表单)', options=["多行", "只有一行"])

        # 输入文本
    File = file_upload(placeholder="请选择PDF表格:", accept='.pdf', str='Choose file', required=True)

        # # 温馨的确认
        # confirm = actions('是否开始转换滴滴出行行程单?',
        #                   [{'label': '确认', 'value': '确认'}, {'label': '取消', 'color': 'warning', 'value': '取消'}],
        #                   help_text='点击后无法取消选择')
        #
        # # 用户搞错了
        # if confirm == '取消':
        #     n += 1
        #     continue
        # # 用户没搞错
        # elif confirm == '确认':
            # 转换成功消息
    toast('⌛超努力转换中！✊', position='center', color='#2188ff', duration=2)
    # 转换工作进度条
    put_processbar(name='bar', auto_close=True)
    for i in range(1, 11):
        set_processbar('bar', i / 10)
        time.sleep(0.1)

    # 生成唯一的文件名
    base_name = os.path.basename(File['filename'])
    name, ext = os.path.splitext(base_name)
    unique_name = f"{name}_{uuid.uuid4().hex}{ext}"

    # 定义下载目录
    download_dir = "/root/Project/SimpleBlog/downloads/"
    # 拼接路径
    download_path = os.path.join(download_dir, unique_name)

    # 保存用户上传的文件到本地项目文件夹下
    with open(download_path, 'wb') as f:
        f.write(File['content'])

    test_tb = camelot.read_pdf(download_path, pages='all', strip_text="\n", flavor='stream', row_tol=8,
                               split_text=True,
                               table_areas=['50,700,537,100'])
    test_list = test_tb[0].data
    flag = test_list[5][0]

    if flag == "序号": # 是多行表
        # 使用camelot从本地项目文件夹下读取文件中的表格
        tables = camelot.read_pdf(download_path, pages='all', strip_text="\n", flavor='stream', row_tol=8,
                                  split_text=True,
                                  table_areas=['50,700,537,100'])
        # print(tables[0].data)

        # 转换表格
        df = []
        i = 0
        for table in tables:
            table.df = table.df.drop(index=[0, 1, 2, 3, 4])
            if i == 0:
                i += 1
                df.append(table.df)
            else:
                table_section = tables[i].data[1:]
                df.append(DataFrame(table_section))
        df = pd.concat(df)

        # 删除多余字段、整理表头
        # df = df.drop(index=[0, 1, 2, 3, 4])
        if df.iloc[0, 7] == '金额[元] 备注':
            df.iloc[0, 7] = '金额[元]'
        if len(df.iloc[0]) == 8:
            df = pd.concat([df, pd.DataFrame(columns=['8'])], sort=False)
            df.iloc[0, 8] = '备注'
        # print(df)

        df = df.fillna(" ")
        if len(tables) > 1:
            df = df[-df[7].str.contains('|'.join(['页码']))]
        # if df[8] == '页码':
        if len(df.iloc[0]) == 8:
            df = df[-df[8].str.contains('|'.join(['页码']))]

    else:
        # 使用camelot从本地项目文件夹下读取文件中的表格
        tables = camelot.read_pdf(download_path, pages='1', strip_text="\n", flavor='stream', row_tol=7,
                                  split_text=True,
                                  table_areas=['56,482,537,380'])

        # 进一步提取表格
        df0 = tables[0].df
        # print(df0)
        df = df0.loc[1:, 0:]
        # print(df)

        # 删除多余字段、整理表头
        for_merge = ['滴滴', '快车']
        substitute_row = df[df[1].isin(for_merge)].sum()
        df.mask(df[1] == "滴滴", substitute_row, axis=1, inplace=True)
        df.drop([3], axis=0, inplace=True)
        # print(df)

        if df.iloc[0, 7] == '金额[元] 备注':
            df.iloc[0, 7] = '金额[元]'
            df[8] = ''
            df.iloc[0, 8] = '备注'
        # print(df)

    # 将转换后的文件以excel格式保存到本地项目文件夹下
    excel_filename = unique_name.replace('.pdf', '.xlsx')
    file_path = os.path.join(download_dir, excel_filename)
    df.to_excel(file_path)
    # "d:/PyProjects/EY_projectplace/xks/downloads/"
    # "/root/Project/SimpleBlog/downloads/"

    # 显示链接供用户下载
    put_markdown(r""" # 👌转换成功！🔔
    """).style('color:green')
    style(put_markdown('*************👇👇👇请下载您的Excel👇👇👇*************'), 'color:red')
    content = open(file_path, 'rb').read()
    put_file(excel_filename, content, r"""👉点击这里下载您的Excel👈""").show()

    # 向用户在线展示转换后的表格
    put_html(df.to_html(index=False, header=None))

    # break


if __name__ == '__main__':
    download_dir = "/root/Project/SimpleBlog/downloads/"

    # 创建静态文件夹，如果不存在的话
    if not os.path.exists(download_dir):
        os.mkdir(download_dir)

    # 开始!
    start_server(main, port=8081, debug=True, cdn=False, auto_open_webbrowser=True)












