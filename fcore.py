import re
from collections import OrderedDict
import requests
import time


def get_response(url, headers, data, timeout):
    for attempt in range(100):
        try:
            response = requests.get(url=url, headers=headers, params=data, timeout=timeout)
            response.raise_for_status()  # 检查响应状态码，如果出现错误会抛出异常
            return response
        except requests.exceptions.RequestException as e:
            print(f"请求尝试 {attempt + 1} 次失败: {e}")
            if attempt < 100:
                print(f"等待 0.1 秒后重新尝试...")
                time.sleep(0.1)
            else:
                print("重试次数已达上限，放弃请求。")
                return None


def get_public_course(cookie, timeout):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
        'Cookie': cookie,
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'http://jwxt.njfu.edu.cn/jsxsd/xsxkkc/comeInGgxxkxk',
    }
    search_data = {
        'kcxx': '',
        'skls': '',
        'skxq': '',
        'endJc': '',
        'skjc': '',
        'sfym': 'false',  # 过滤已满
        'sfct': 'true',  # 过滤冲突
        'szjylb': '',
        'sfxx': 'true',  # 过滤限选
        'skfs': '',
        'sEcho': 1,
        'iColumns': 12,
        'sColumns': 12,
        'iDisplayStart': 0,
        'iDisplayLength': 999,  # 一次获取多少课程的信息
        'mDataProp_0': 'kch',
        'mDataProp_1': 'kcmc',
        'mDataProp_2': 'xf',
        'mDataProp_3': 'skls',
        'mDataProp_4': 'sksj',
        'mDataProp_5': 'skdd',
        'mDataProp_6': 'xqmc',
        'mDataProp_7': 'xkrs',
        'mDataProp_8': 'syrs',
        'mDataProp_9': 'ctsm',
        'mDataProp_10': 'tsTskflMc',
        'mDataProp_11': 'czOper'
    }
    url = f'http://jwxt.njfu.edu.cn/jsxsd/xsxkkc/xsxkGgxxkxk?kcxx=&skls=&skxq=&endJc=&skjc=&sfym={search_data["sfym"]}&sfct={search_data["sfct"]}&szjylb=&sfxx={search_data["sfxx"]}&skfs='
    response = get_response(url=url, headers=headers, data=search_data, timeout=timeout)
    if response.ok:
        dic = response.json()
        course_lis = []
        if 'aaData' in dic:
            for i, info in enumerate(dic['aaData']):
                # 处理教师姓名
                if 'kkapList' in info:
                    teacher_name = info['kkapList'][0]['jgxm']
                    if teacher_name == '':
                        teacher_name = '未知'
                else:
                    teacher_name = '未知'

                course_dic = OrderedDict({
                    'Name': info['kcmc'],
                    'Teacher': teacher_name,
                    'Credits': info['xf'],
                    'Type': info['kcsxmc'],
                    'Left': info['syrs'],
                    '02id': info['jx02id'],
                    '04id': info['jx0404id'],
                    'kch': info['kch'],
                })
                course_lis.append(course_dic)
            return course_lis
        else:
            return None
    else:
        return None


def get_pe_course(cookie, class_num, timeout):
    url = 'http://jwxt.njfu.edu.cn/jsxsd/xsxkkc/xsxkBxxk?1=1&kcxx=&skls=&skfs='
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
        'Cookie': cookie,
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'http://jwxt.njfu.edu.cn/jsxsd/xsxkkc/comeInBxxk',
    }
    search_data = {
        '1': '1',
        'kcxx': '',
        'skls': '',
        'skfs': '',
        'sEcho': '1',
        'iColumns': '14',
        'sColumns': '',
        'iDisplayStart': '0',
        'iDisplayLength': '200',  # 一次获取的课程数
        'mDataProp_0': 'kch',
        'mDataProp_1': 'kcmc',
        'mDataProp_2': 'dwmc',
        'mDataProp_3': 'skfsmc',
        'mDataProp_4': 'fzmc',
        'mDataProp_5': 'ktmc',
        'mDataProp_6': 'xf',
        'mDataProp_7': 'skls',
        'mDataProp_8': 'sksj',
        'mDataProp_9': 'skdd',
        'mDataProp_10': 'xqmc',
        'mDataProp_11': 'syrs',
        'mDataProp_12': 'ctsm',
        'mDataProp_13': 'czOper',
    }

    response = get_response(url=url, headers=headers, data=search_data, timeout=timeout)
    if response is not None:
        dic = response.json()
        course_lis = []
        if 'aaData' in dic:
            for i, info in enumerate(dic['aaData']):
                # 冲突课程直接跳过
                unavailable = info['ctsm']
                if unavailable != '':
                    continue
                # 非本班的课程直接跳过
                classes = info['ktmc']
                pattern = r'\[(.*?)-(.*?)\]'
                matches = re.findall(pattern, classes)
                in_range = False
                for match in matches:
                    if (class_num >= match[0]) & (class_num <= match[1]):
                        in_range = True
                        break
                if not in_range:
                    continue

                # 处理上课老师姓名
                if 'kkapList' in info:
                    teacher_name = info['kkapList'][0]['jgxm']
                    if teacher_name == '':
                        teacher_name = '无'
                else:
                    teacher_name = '未知'
                # 把课程信息添加到列表
                course_dic = OrderedDict({
                    'Name': info['fzmc'],
                    'Teacher': teacher_name,
                    'Credits': info['xf'],
                    'Type': info['kcsxmc'],
                    'Left': info['syrs'],
                    '02id': info['jx02id'],
                    '04id': info['jx0404id'],
                    'kch': info['kch'],
                })
                course_lis.append(course_dic)
            return course_lis
        else:
            return None
    else:
        return None


def select_course(cookie, id02, id04, name, is_public, timeout):
    referer_arg = 'Bxxk'
    url_arg = 'bxxk'
    if is_public:
        referer_arg = 'Ggxxkxk'
        url_arg = 'ggxxkxk'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
        'Cookie': cookie,
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': f'http://jwxt.njfu.edu.cn/jsxsd/xsxkkc/comeIn{referer_arg}',
    }
    data = {
        'kcid': f'{id02}',
        'cfbs': 'null',
        'jx0404id': f'{id04}',
        'xkzy': '',
        'trjf': ''
    }
    url = f'http://jwxt.njfu.edu.cn/jsxsd/xsxkkc/{url_arg}Oper?kcid={id02}&cfbs=null&jx0404id={id04}&xkzy=&trjf='
    response = get_response(url=url, headers=headers, data=data, timeout=timeout)
    result = response.json()
    if 'success' in result:
        return f'{name} {result['message']}'
    else:
        return 'Cookie已过期,请返回上一界面重新进入'
