import inspect
import random
import string
from enum import Enum
from typing import Any, Dict, Union, Optional, Tuple

import requests


def generate_random_string(length: int = 10) -> str:
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

    def __init__(self, base_url: str = "public.ghs.wiki:7001") -> None:
        self.base_url = base_url
        self.token = ""
        self.enable_simple_return = False

    def send_msg(self, request_type: Union[str, Enum], token: bool = True, **kwargs) -> DynamicClass:
        """发送请求消息并返回响应。

        参数:
            request_type (Union[str, Enum]): 请求类型，可以是字符串或枚举类型。
            token (bool): 是否需要token，默认为True。
            **kwargs: 请求参数。

        返回:
            DynamicClass: 响应的动态类对象。
        """
        if isinstance(request_type, Enum):
            request_type = request_type.value
        url = f"http://{self.base_url}/API?type={request_type}"
        if token:
            url += f"&token={self.token}"
        for key, value in kwargs.items():
            url += f"&{key}={value}"
        response = requests.post(url)
        return DynamicClass(response.json())

    def process_result_normal(self, code: int, result_type: str) -> Union[str, bool]:
        """处理普通结果。

        参数:
            code (int): 响应状态码。
            result_type (str): 结果类型。

        返回:
            Union[str, bool]: 处理后的结果。
        """
        if self.enable_simple_return:
            result_str = getattr(StatusParser, result_type, None)
            if result_str is None:
                return StatusParser.general.get(result_type, False)
            return result_str
        else:
            if code != 200:
                return False
            return True

    def process_result(self, code: Union[int, DynamicClass], special: bool = False, special_key: str = "") -> Union[str, bool]:
        """处理结果。

        参数:
            code (Union[int, DynamicClass]): 响应状态码或动态类对象。
            special (bool): 是否处理特殊结果，默认为False。
            special_key (str): 特殊结果的键名，默认为空。

        返回:
            Union[str, bool]: 处理后的结果。
        """
        if special:
            if special_key == "":
                raise Exception("当special为True时special_key不能为空")
            return getattr(code, special_key, None)
        else:
            if isinstance(code, DynamicClass):
                code = getattr(code, "status", 616)
            return self.process_result_normal(code, result_type=inspect.stack()[1].function)

    def login(self, username: str, passwd: str) -> Union[str, bool]:
        """登录。

        参数:
            username (str): 用户名。
            passwd (str): 密码。

        返回:
            Union[str, bool]: 登录结果。
        """
        result = self.send_msg(RequestTypes.login, account=username, password=passwd, token=False)
        return self.process_result(result)

    def send_verify_msg(self, email: str, key: str) -> Union[str, bool]:
        """发送验证消息。

        参数:
            email (str): 邮箱地址。
            key (str): 验证码。

        返回:
            Union[str, bool]: 发送结果。
        """
        result = self.send_msg(RequestTypes.verify, email=email, key=key)
        return self.process_result(result)

    def register(self, email: str, username: str, passwd: str, code: str) -> Union[str, bool]:
        """注册。

        参数:
            email (str): 邮箱地址。
            username (str): 用户名。
            passwd (str): 密码。
            code (str): 验证码。

        返回:
            Union[str, bool]: 注册结果。
        """
        result = self.send_msg(RequestTypes.register, email=email, username=username, password=passwd, code=code)
        return self.process_result(result)

    def get_user_info(self) -> Union[DynamicClass, bool]:
        """获取用户信息。

        返回:
            Union[DynamicClass, bool]: 用户信息或获取结果。
        """
        result = self.send_msg(RequestTypes.get_user_info)
        info = getattr(result, "userInfo", None)
        if info is None:
            return False
        return DynamicClass(info)

    def get_all_nodes(self) -> Union[str, bool]:
        """获取所有节点。

        返回:
            Union[str, bool]: 获取结果。
        """
        result = self.send_msg(RequestTypes.get_all_nodes)
        return self.process_result(result, special=True, special_key="nodeData")

    def get_user_nodes(self) -> Optional[Tuple[str, str]]:
        """获取用户穿透码。

        返回:
            Optional[Tuple[str, str]]: 用户节点。
        """
        result = self.send_msg(RequestTypes.get_user_codes)
        data = self.process_result(result, special=True, special_key="codeData")
        if isinstance(data, dict):
            return data.items()

    def remove_code(self, node: str, code: str) -> Union[str, bool]:
        """移除穿透码。

        参数:
            node (str): 节点。
            code (str): 穿透码。

        返回:
            Union[str, bool]: 移除结果。
        """
        result = self.send_msg(RequestTypes.register, node=node, number=code)
        return self.process_result(result)