import os
import pandas as pd
from pandas.core.frame import DataFrame

def set_cost():
    cost_list = list()
    print('[*]在數字後面補上「+」，即可設定均一價。')
    print('[*]例如: 1000+ ，等於是設定均一價為1000元。')

    for years_old in ('3歲以下', '4~6歲', '7~12歲', '13~64歲', '65歲以上'):
        _in = input(f'[?]{years_old}報價: ')
        if '+' in _in:
            return [int(_in.removesuffix('+')) for _ in range(5)]
        else:
            try:
                cost_list.append(int(_in))
            except ValueError:
                is_digit = False
                while not is_digit:
                    _in = input('[!]請輸入數字...  : ')
                    if '+' in _in:
                        return [int(_in.removesuffix('+')) for _ in range(5)]
                    is_digit = True
    return cost_list

def clearConsole() -> None:
    command = "clear"
    if os.name in ("nt", "dos"):  # If Machine is running on Windows, use cls
        command = "cls"
    os.system(command)

def xlsx_DataFrame(clientList: list, mode: str) -> DataFrame:
    """
    MODE:
     - including_roomType
     - excluding_roomType
    """
    if mode == "including_roomType":
        return pd.DataFrame(
            {
                "姓名": [client.name for client in clientList],
                "身分證字號": [client.id for client in clientList],
                "生日": [client.birthday for client in clientList],
                "年齡": [client.yearsOld for client in clientList],
                "電話": [client.phone for client in clientList],
                "上車點": [client.location for client in clientList],
                "餐食": [client.foodType for client in clientList],
                "特殊需求": [client.specialNeeds for client in clientList],
                "房型": [client.roomType for client in clientList],
                "同房者": [client.roommate for client in clientList],
                "團費": [client.cost for client in clientList],
                "折扣碼": [client.discountUsed for client in clientList],
                "社群暱稱": [client.nickName for client in clientList],
                "警告訊息": [client.alertMsg for client in clientList]
            }
        )
    elif mode == "excluding_roomType":
        return pd.DataFrame(
            {
                "姓名": [client.name for client in clientList],
                "身分證字號": [client.id for client in clientList],
                "生日": [client.birthday for client in clientList],
                "年齡": [client.yearsOld for client in clientList],
                "電話": [client.phone for client in clientList],
                "上車點": [client.location for client in clientList],
                "餐食": [client.foodType for client in clientList],
                "特殊需求": [client.specialNeeds for client in clientList],
                "團費": [client.cost for client in clientList],
                "折扣碼": [client.discountUsed for client in clientList],
                "社群暱稱": [client.nickName for client in clientList],
                "警告訊息": [client.alertMsg for client in clientList]
            }
        )
    else:
        print("[!]函數 xlsx_DataFrame 的參數 mode 錯誤")
        os.system("pause")
        raise BaseException

def default():
    print("請重新選擇功能")