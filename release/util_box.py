import json
import os
import numpy as np
import pandas as pd
import opencc
from lxml import etree
from matplotlib import pyplot as plt
import seaborn as sns


def paint_single_violin_graph(data_list, title):
    # 构件图
    fig, ax = plt.subplots(1, 1, figsize=(8, 5))
    type_fontsize = 20
    # 绘制图形
    sns.violinplot(y=data_list, ax=ax)
    ax.set_title(title, fontsize=type_fontsize)
    ax.set_ylabel(title, color='k', fontsize=12)
    plt.show()


def write_txt_a(txt_filename, content):
    with open(txt_filename, 'a', encoding='utf-8') as f:
        f.write(content)
        f.close()
    print('\n')
    print('add txt file to:', txt_filename)


def write_txt_w(txt_filename, content):
    with open(txt_filename, 'w', encoding='utf-8') as f:
        f.write(content)
        f.close()
    print('\n')
    print('write txt file to:', txt_filename)


def read_txt(read_path):
    with open(read_path, 'r', encoding='utf-8') as f:
        data = f.read()
        f.close()
    print('\n')
    print('read txt file from:', read_path)
    return data


def write_json_w(write_path, data):
    with open(write_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
        f.close()
    print('\n')
    print('write json file to:', write_path)


def write_json(write_path, data):
    with open(write_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
        f.close()
    print('\n')
    print('write json file to:', write_path)


def read_json(read_path):
    with open(read_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        f.close()
    print('\n')
    print('read json file from:', read_path)
    return data


def str2json(str_json):
    json_data = json.loads(str_json)
    return json_data


def pd_read_csv(read_path, encoding='utf-8'):
    data = pd.read_csv(read_path, encoding=encoding)
    print('\n')
    print('read csv file from:', read_path)
    return data


def pd_read_excel(read_path):
    data = pd.read_excel(read_path, sheet_name='Sheet1', index_col=0)
    print('\n')
    print('read excel file from:', read_path)
    return data


def pd_write_csv(data_dict, write_path, index=False):
    df = pd.DataFrame(data_dict)
    df.to_csv(write_path, index=index)
    print('\n')
    print('write csv file to:', write_path)


def pd_write_excel(data_dict, write_path, index=False):
    df = pd.DataFrame(data_dict)
    df.to_excel(write_path, index=index)
    print('\n')
    print('write excel file to:', write_path)


def is_file_exist(path):
    return os.path.exists(path)


def add_item2dict(dic, item):
    if item in dic:
        dic[item] += 1
    else:
        dic[item] = 1


def write_statistics_dict(dict_for_statistics, statistics_write_path, reverse_sort=True):
    # 首先排序，默认倒序
    dict_for_statistics = sorted(dict_for_statistics.items(), key=lambda x: x[1], reverse=reverse_sort)
    # 然后写成list
    list_for_statistics = ['{}\t{}'.format(item[0], int(item[1])) for item in dict_for_statistics]
    # 最后写入文件
    write_txt_w(statistics_write_path, '\n'.join(list_for_statistics))


def write_statistics_dict_no_fre(dict_for_statistics, statistics_write_path, reverse_sort=True):
    # 首先排序，默认倒序
    dict_for_statistics = sorted(dict_for_statistics.items(), key=lambda x: x[1], reverse=reverse_sort)
    # 然后写成list
    list_for_statistics = ['{}'.format(item[0]) for item in dict_for_statistics]
    # 最后写入文件
    write_txt_w(statistics_write_path, '\n'.join(list_for_statistics))


def write_item2dict(dic, item):
    if item in dic:
        dic[item] += 1
    else:
        dic[item] = 1


def write_html(content, name, output_dir_):
    name = name.replace('/', '')
    name_ = name+'.html'
    fo = open(output_dir_+name_, "w", encoding='UTF-8')
    fo.write("<html>")
    fo.write("<meta charset=\"utf-8\">")
    fo.write("<body>")
    fo.write(content)
    fo.write("</body>")
    fo.write("</html>")
    fo.close()


def is_letter(ch):  # 判断一个unicode是否是英文字母
    if (u'\u0041' <= ch <= u'\u005a') or (u'\u0061' <= ch <= u'\u007a'):
        return True
    else:
        return False


def is_chinese(uchar):  # 判断一个unicode是否是汉字
    if u'\u4e00' <= uchar <= u'\u9fa5':
        return True
    else:
        return False


def is_digit(uchar):  # 判断一个unicode是否是数字
    if u'\u0030' <= uchar <= u'\u0039':
        return True
    else:
        return False


# 判断是否是（汉字，数字和英文字符之外的）其他字符
def is_other(uchar):
    if not (is_chinese(uchar) or is_digit(uchar) or is_letter(uchar)):
        return True
    else:
        return False


def traditional2simplified(sentence):
    cc = opencc.OpenCC('t2s')
    sentence = cc.convert(sentence)
    return sentence


# HTML parsing
def html_parsing(html_str, tag=None):
    # tag: h1, strong, p, div, span, etc.
    root = etree.HTML(html_str)
    if tag is not None:
        tag_texts = root.xpath('//'+tag+'/text()')
        tag_texts = [str(text) for text in tag_texts]
    else:
        tag_texts = root.xpath('//text()')
        tag_texts = [str(text) for text in tag_texts]
    return tag_texts


def html_tag_clean(html_str):
    root = etree.HTML(html_str)
    etree_texts = root.xpath('//text()')
    texts = [str(text) for text in etree_texts]
    clean_str = ''.join(texts)
    return clean_str


def html_tag_finding(html_str):
    # find all tags in html
    root = etree.HTML(html_str)
    html_tags = root.xpath('//*')  # HTML中所有的标签list
    tags_list = []
    for html_tag in html_tags:
        # get the tag info of each element
        tag_info = {
            'tag': html_tag.tag,
            # 'attrib': html_tag.attrib,
            'text': html_tag.text
        }
        # add2list
        tags_list.append(tag_info)
    return tags_list


def html_table_parsing(html_str):
    # find all tables in html
    root = etree.HTML(html_str)
    html_tables = root.xpath('//table')  # HTML中所有的表格list
    table_info_list = []
    for html_table in html_tables:
        # 将第一个表格转成string格式
        table = etree.tostring(html_table, encoding='utf-8').decode()  # table:html格式的str
        # pandas读取table
        if '</tbody>' not in table:  # 有些表格式为<table ... /> 解析会出错
            continue
        # print(table)
        df = pd.read_html(table, encoding='utf-8')
        if len(df) == 0:
            continue
        df = df[0]
        # 遍历所有的值，如果是nan，就替换成空字符串 or 'None'
        for i in range(len(df)):
            for j in range(len(df.columns)):
                if pd.isna(df.iloc[i, j]):
                    df.iloc[i, j] = 'None'
        # print(df)
        # 表至少得有两列，否则不处理
        if len(df.columns) < 2:
            continue
        # 添加表头，第一列是node，后面依次是attr1, attr2, ...
        # # 保留原来的表头作为一行数据，添加到表格的最后一行
        # df.loc[-1] = df.columns
        df.columns = ['node'] + ['attr'+str(i) for i in range(1, len(df.columns))]
        # 把第一列的值作为index
        df.set_index('node', inplace=True)
        # # 交换第一行和最后一行的数据，中间不变，用pandas.concat函数实现
        # df = pd.concat([df.iloc[-1:], df.iloc[:-1]])
        # 去掉第一行数据
        df = df.iloc[1:]
        # print(df)
        # 转换成列表嵌套字典的格式
        results = list(df.to_dict().values())
        # print(results)
        # 合并这些字典，把相同key的value合并成一个list，警惕key或value为nan的情况
        fusion_result = {key: [dic[key] for dic in results if dic[key] is not np.nan] for key in results[0] if key is not np.nan and not isinstance(key, int)}
        # print(fusion_result)
        # 最后能够看到一个包含很多字典的list
        table_info_list.append(fusion_result)
    return table_info_list


def test():
    pass


if __name__ == '__main__':
    test()
