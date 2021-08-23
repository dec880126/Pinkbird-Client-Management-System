import os
import pandas as pd
from pandas.core.frame import DataFrame

def set_cost():
    cost_3 = int(input('[?]3歲以下報價: '))
    cost4to6 = int(input('[?]4~6歲報價: '))
    cost7to12 = int(input('[?]7~12歲報價: '))
    cost13to64 = int(input('[?]13~64歲報價: '))
    cost65 = int(input('[?]65歲以上報價: '))
    # cost_3 = 0
    # cost4to6 = 500
    # cost7to12 = 1000
    # cost13to64 = 1500
    # cost65 = 1000
    return [cost_3, cost4to6, cost7to12, cost13to64, cost65]

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