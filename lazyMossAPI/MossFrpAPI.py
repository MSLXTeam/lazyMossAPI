import inspect
import random
import string
from enum import Enum
from typing import Any, Dict, Union

import requests


def generate_random_string(length=10) -> str:
    """生成一个指定长度的随机字符串。

    默认长度是10。字符串包括大写字母、小写字母和数字。

    参数:
        length (int): 随机字符串的长度。默认是10。

    返回:
        str: 生成的随机字符串。
    """
    characters = string.ascii_letters + string.digits  # 包括大写字母、小写字母和数字
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


class DynamicClass:
    def __init__(self, data: Dict[str, Any]) -> None:
        """初始化一个动态类，将字典的键值对转换为类的属性"""
        self.__dict__.update(data)


class ProxyTypes(Enum):
    """代理类型枚举"""
    tcp = "tcp"
    udp = "udp"
    http = "http"
    https = "https"
    stcp = "stcp"
    xtcp = "xtcp"


class RequestTypes(Enum):
    """请求类型枚举"""

    # 用户相关
    login = "login"
    verify = "verification"
    register = "register"
    update_user_info = "infoUpdate"
    get_user_info = "userInfo"

    # 穿透码相关
    get_user_codes = "userCode"
    get_all_nodes = "allNode"
    remove_code = "removeCode"
    create_code = "createCode"
    date_code = "dateCode"
    band_code = "bandCode"


class StatusParser:
    """保存Status值特殊含义"""
    general = {400: "参数错误/参数不足", 401: "Token错误/缺失,请尝试重新登陆",
               423: "Congratulations!你的IP被ban了,可能是因为你短时间内发送了大量请求导致被视为恶意攻击"}
    register = {403: "传入信息有误", 404: "验证码错误"}


class MossFrpAPI:

    def __init__(self, base_url: str = "public.ghs.wiki:7001"):
        self.base_url = base_url
        self.token = ""
        self.enable_simple_return = False

    def send_msg(self, request_type: Union[str, Enum], token: bool = True, **kwargs):
        if isinstance(request_type, Enum):
            request_type = request_type.value
        url = f"http://{self.base_url}/API?type={request_type}"
        if token:
            url += f"&token={self.token}"
        for key, value in kwargs.items():
            url += f"&{key}={value}"
        response = requests.post(url)
        return DynamicClass(response.json())

    def process_result_normal(self, code, result_type):
        if self.enable_simple_return:
            result_str = getattr(StatusParser, result_type, None)
            if result_str is None:
                return StatusParser.general.get(result_type, False)
            return result_str
        else:
            if code != 200:
                return False
            return True

    def process_result(self, code: Union[int, DynamicClass], special: bool = False, special_key: str = "") -> (
            Union)[str, bool]:
        if special:
            if special_key == "":
                raise Exception("当special为True时special_key不能为空")
            return getattr(code, special_key, None)
        else:
            if isinstance(code, DynamicClass):
                code = getattr(code, "status", 616)
            return self.process_result_normal(code, result_type = inspect.stack()[1].function)

    def login(self, username: str, passwd: str):
        result = self.send_msg(RequestTypes.login, account=username, password=passwd, token=False)
        return self.process_result(result)

    def send_verify_msg(self, email: str, key: str):
        result = self.send_msg(RequestTypes.verify, email=email, key=key)
        return self.process_result(result)

    def register(self, email: str, username: str, passwd: str, code: str) -> Union[str, bool]:
        result = self.send_msg(RequestTypes.register, email=email, username=username, password=passwd, code=code)
        return self.process_result(result)

    def get_user_info(self):
        result = self.send_msg(RequestTypes.get_user_info)
        info = getattr(result, "userInfo", None)
        if info is None:
            return False
        return DynamicClass(info)

    def get_all_nodes(self):
        result = self.send_msg(RequestTypes.get_all_nodes)
        return self.process_result(result, special=True, special_key="nodeData")

    def get_user_nodes(self):
        result = self.send_msg(RequestTypes.get_user_codes)
        data = self.process_result(result, special=True, special_key="codeData")
        if isinstance(data, dict):
            return data.items()

    def remove_code(self, node: str, code: str):
        result = self.send_msg(RequestTypes.register, node=node, number=code)
        return self.process_result(result)

