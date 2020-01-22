import io
import os
from datetime import datetime

from jinja2 import Template

from httprunner import logger
from httprunner.exceptions import SummaryEmpty

import requests
import json
from datetime import datetime

def gen_html_report(summary, report_template=None, report_dir=None, report_file=None):
    """ render html report with specified report name and template

    Args:
        summary (dict): test result summary data
        report_template (str): specify html report template path, template should be in Jinja2 format.
        report_dir (str): specify html report save directory
        report_file (str): specify html report file path, this has higher priority than specifying report dir.

    """
    if not summary["time"] or summary["stat"]["testcases"]["total"] == 0:
        logger.log_error("test result summary is empty ! {}".format(summary))
        raise SummaryEmpty

    if not report_template:
        report_template = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "template.html"
        )
        logger.log_debug("No html report template specified, use default.")
    else:
        logger.log_info("render with html report template: {}".format(report_template))

    logger.log_info("Start to render Html report ...")

    start_at_timestamp = summary["time"]["start_at"]
    utc_time_iso_8601_str = datetime.utcfromtimestamp(start_at_timestamp).isoformat()
    summary["time"]["start_datetime"] = utc_time_iso_8601_str

    if report_file:
        report_dir = os.path.dirname(report_file)
        report_file_name = os.path.basename(report_file)
    else:
        report_dir = report_dir or os.path.join(os.getcwd(), "reports")
        # fix #826: Windows does not support file name include ":"
        report_file_name = "{}.html".format(utc_time_iso_8601_str.replace(":", "").replace("-", ""))

    if not os.path.isdir(report_dir):
        os.makedirs(report_dir)

    report_path = os.path.join(report_dir, report_file_name)
    with io.open(report_template, "r", encoding='utf-8') as fp_r:
        template_content = fp_r.read()
        with io.open(report_path, 'w', encoding='utf-8') as fp_w:
            rendered_content = Template(
                template_content,
                extensions=["jinja2.ext.loopcontrols"]
            ).render(summary)
            fp_w.write(rendered_content)

    logger.log_info("Generated Html report: {}".format(report_path))


    # 把报告上传到ftp存储
    report_path = save_report_to_ftp(report_path)

    # 数据拼接发送到企业微信
    try:
        successes =  summary['stat']['teststeps']['successes']
    except Exception as e:
        successes = 0

    total = summary['stat']['teststeps']['total']
    failures = summary['stat']['teststeps']['failures']
    errors = summary['stat']['teststeps']['errors']
    skipped =summary['stat']['teststeps']['skipped']
    parameters = {}
    parameters[
        'body'] = '结果汇总：\n时间: {timestamp}\n累计: {total}个\n成功: {successes}个\n失败: {failures}个\n错误: {errors}个\n报告地址：{report_path}' \
        .format(timestamp=get_current_date(fmt="%Y-%m-%d %H:%M:%S"),total=total, successes=successes, failures=failures, errors=errors,report_path=report_path)
    logger.log_debug(parameters['body'])
    send_wechat_message(parameters['body'])

    return report_path


def send_wechat_message(message_text):
    """"
    发送企业微信机器人消息
    :param platform:
    :param app_version:
    :param tag:
    :param env:
    :param app_path:
    :return:
    """



    message_text = '*************************** 接口自动化测试服务报警 ***************************************' + '\n' + \
                   message_text + '\n' + \
                   '***************************************************************************************'
    try:

        webhook_api = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=a0a3bd2c-268c-4134-ba67-ae83a8fe1d68"  # 单独的接口自动化测试群
        data = {
            "msgtype": "text",
            "text": {
                "content": message_text,
            }
        }
        logger.log_debug(json.dumps(message_text,indent=4))
        r = requests.post(webhook_api, json=data, verify=False)
        logger.log_info(str(r.status_code))
    except Exception as e:
        logger.log_error(str(e))


def save_report_to_ftp(report_path):
    """
    当报告失败后,保存失败的报告保存到ftp中
    :return:
    """

    logger.log_info('post local report' + '\n' + str(report_path))
    url = "http://127.0.0.1:5000/uploadfile"
    file_path = ''
    try:
        payload = {}
        files = {'file': open(report_path, 'rb')}
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.post(url, files=files, verify=False)
        if response.status_code == 200:
            file_path = str(response.json()['file_path'])
            logger.log_info('save report ftp path is: {}'.format(file_path))
        else:
            logger.log_info(str(response.status_code) + '\n' + str(response.text))
    except Exception as e:
        logger.log_info('post report error!{}'.format(str(e)))
    finally:
        return file_path



def get_current_date(fmt="%Y-%m-%d"):
    """ get current date, default format is %Y-%m-%d
    """
    return datetime.now().strftime(fmt)