"""
PINKBIRD TRAVEL CLIENT DATABASE SYSTEM

Copyright (c) 2021 CyuanHuang

FUNCTION LIST:
 - Departure clients' infomation list generator
 - Discount code generator
 - Clients' profiler editor
 - Add NEW Clients' profile
 - Check if the data is duplicated in the database

ALL OF THE FUNCTION PROVIDED ARE WORKING BASE ON SQL(Structured Query Language)
"""
import pandas as pd
from pandas.core.frame import DataFrame
import pymysql
import datetime
import sys
import os
import string
import secrets

import package.year_cal as year_cal
import package.config as config

programVersion = "版本: " + "5.0"

class Client():
    """
    default setting:

     - self.name = "無"
     - self.id = "無"
     - self.birthday = "無"
     - self.phone = "無"
     - self.location = "無"
     - self.foodType = "無"
     - self.specialNeeds = "無"
     - self.roomType = "無"
     - self.roommate = "無"
     - self.cost = "無"
     - self.discountCode = "無"
     - self.discountUsed = "無"
     - self.nickName = "無"
     - self.alertMsg = "無"
     - self.yearsOld = "無"
     - self.travelDays = 0
    """
    def __init__(self) -> None:
        # , name, id, birthday, phone, location, foodType, specialNeeds, roomType, roommate, cost, discountCode, discountUsed, nickName, alertMsg
        self.name = "無"
        self.id = "無"
        self.birthday = "無"
        self.phone = "無"
        self.location = "無"
        self.foodType = "無"
        self.specialNeeds = "無"
        self.roomType = "無"
        self.roommate = "無"
        self.cost = "無"
        self.discountCode = "無"
        self.discountUsed = "無"
        self.nickName = "無"
        self.alertMsg = "無"
        self.yearsOld = "無"
        self.travelDays = 0

class Code():
    def __init__(self, code, value, clientName, deadline, generateBy, generateTime) -> None:
        self.code = code
        self.value = value
        self.clientName = clientName
        self.deadline = deadline
        self.generateBy = generateBy
        self.generateTime = generateTime

class Endding(Exception):
    def __init__(self):
        sys.exit()

class WrongDepartTypeChoose(Exception):
    def __init__(self):
        pass

class GetOutOfTryExcept(Exception):
    def __init__(self):
        pass

def searchCommand(listFrom: str, key: str, searchBy) -> str:
    """
    根據輸入列表，產生搜尋的SQL指令

    SELECT * FROM `會員資料` WHERE '身分證字號' = '~~'

    使用範例: searchCommand(listFrom="會員資料", key="身分證字號", searchBy = idList)
    """
    # 如果輸入是單一資料
    if isinstance(searchBy, str):
        temp = searchBy
        tempList = [temp]
        searchBy = tempList.copy()

    commandEnd = str(tuple(searchBy))

    # 如果輸入是List
    if commandEnd[-2] == ',':
        temp = list(commandEnd)
        temp[-2] = ''
        commandEnd = ''.join(temp)
    return "SELECT * FROM `" + listFrom + "` WHERE `" + key + "` IN " + commandEnd

def listAllCommand(listFrom: str) -> str:
    """
    根據輸入所給之資料表名稱，產生列出所有資料之SQL指令

    SELECT * FROM `會員資料`
    """
    return "SELECT * FROM `" + str(listFrom) + "`"

def deleteCommand(listFrom: str, key: str, value: str) -> str:
    """
    根據輸入所之資料表，產生刪除對應資料之SQL指令

    DELETE FROM `會員資料` WHERE '姓名' = '王小明'
    """
    return f"DELETE FROM `{str(listFrom)}` WHERE `{key}` = '{value}'"

def insertCommand(listFrom: str, key: tuple, value: tuple) -> str:
    """
    產生加入新資料之SQL指令

    INSERT INTO `會員資料` (`姓名`, `身分證字號`, `生日`, `電話`, `餐食`, `特殊需求`, `暱稱`, `旅遊天數`) VALUES ([value-1],[value-2],[value-3],[value-4],[value-5],[value-6],[value-7],[value-8])
    """
    singleQuote = "\'"
    backQuote = "`"
    return f"INSERT INTO `{str(listFrom)}` {str(key).replace(singleQuote, backQuote)} VALUES {str(value)}"

def editCommand(listFrom: str, key_toUpdate: list, value_toUpdate: list, searchBy_key: list, searchBy_value: list) -> str:
    """
    UPDATE `旅遊金序號` SET `是否使用過`=0 WHERE `序號` = '120288878ZJtKV';
    """
    return "UPDATE `" + str(listFrom) + "` SET `" + str(key_toUpdate) + "`='" + str(value_toUpdate) + "' WHERE `" + str(searchBy_key) + "` = '" + str(searchBy_value) + "'"

def registeForm_processing():
    # <---------- departMode selecting start ---------->
    print("[*]====================出團模式選擇====================")
    print("[*]模式選項: ")
    print("[*]  1. 報名表單「不」包含房型選項")
    print("[*]  2. 報名表單包含房型選項")    
    print("[*]===================================================")
    while True:
        try:
            departMode = int(input("[?]請選擇出團模式: "))
        except ValueError:
            print("[!]請先選擇出團模式!")
            os.system("pause")
            continue
        if departMode in (1, 2):
            pass
            break
        else:
            print("[!]請重新輸入正確的選項....")
            os.system("pause")
    # <---------- departMode selecting end ---------->
            
    # <---------- reading xlsx start ---------->
    filePath = input('[?]請將檔案拉到程式畫面中...')
    try:
        if departMode == 1:
            df = pd.read_excel(
                filePath,
                sheet_name="表單回應 1",
                usecols="B:E",  # B:E順序為: "身分證字號", "連絡電話", "上車地點", "序號"
            )
        elif departMode == 2:
            df = pd.read_excel(
                filePath,
                sheet_name="表單回應 1",
                usecols="B:G",  # B:G順序為: "身分證字號", "連絡電話", "上車地點", "房型", "同房者", "序號"
            )
    except OSError:
        clearConsole()
        print("[*]========================================================================================")
        print("[!]警告: 由於 Windows 系統不支援檔案名稱中有空格的程式操作 請將檔案名稱中的空格刪除後再重新執行")        
        print("[*]========================================================================================")
        print("[*]幫助: 範例: 粉鳥旅行社多日遊報名表單範例 (回覆).xlsx    <- 此為檔案名稱")
        print("[*]           通常空格存在於「(回覆)」的前面，刪除空格後程式即可正常執行!")
        print("[!]提醒: 空格的原因是因為 Goolge 端的設定就是這樣，所以以後在匯入前要留意一下")
        print("[*]========================================================================================")
        input("[*]請按任意鍵回到 粉鳥旅行社會員資料庫管理系統-功能選擇介面...")
        return
    # <---------- reading xlsx end ---------->

    # <---------- depart info start ---------->
    while True:
        departDay_raw = input('[?]請輸入出團日期(YYYY.MM.DD)： ').split(".")

        try:
            departDay = datetime.date(
                year=int(departDay_raw[0]),
                month=int(departDay_raw[1]),
                day=int(departDay_raw[2])
            )
            break
        except IndexError:
            print("[!]日期輸入格式錯誤，請重新輸入，並確認格式為: YYYY.MM.DD")

    travelDays = int(input('[?]此次出團為幾日團(輸入數字)? '))

    costList = set_cost()
    # <---------- depart date info end ---------->

    # <---------- client class processing start ---------->
    # registerForm_List = []  # 報名表單的客戶清單 -> class
    attendClient_Dict = {}  # 參加的客戶清單 -> class
    
    if departMode == 1:
        for idx in range(df.shape[0]):
            IDhere = df.at[idx, df.columns[0]]
            attendClient_Dict[IDhere] = Client()

            attendClient_Dict[IDhere].id = IDhere
            attendClient_Dict[IDhere].phone = df.at[idx, df.columns[1]]
            attendClient_Dict[IDhere].location = df.at[idx, df.columns[2]]
            attendClient_Dict[IDhere].roomType = None
            attendClient_Dict[IDhere].roommate = None
            attendClient_Dict[IDhere].discountCode = str(df.at[idx, df.columns[5]])
    elif departMode == 2:
        for idx in range(df.shape[0]):
            IDhere = df.at[idx, df.columns[0]]
            attendClient_Dict[IDhere] = Client()

            attendClient_Dict[IDhere].id = df.at[idx, df.columns[0]]
            attendClient_Dict[IDhere].phone = df.at[idx, df.columns[1]]
            attendClient_Dict[IDhere].location = df.at[idx, df.columns[2]]
            attendClient_Dict[IDhere].roomType = df.at[idx, df.columns[3]]
            attendClient_Dict[IDhere].roommate = df.at[idx, df.columns[4]]
            attendClient_Dict[IDhere].discountCode = str(df.at[idx, df.columns[5]])
    # <---------- client class processing end ---------->

    try:
        cursor = conn.cursor()
        print(f"[-]正在向資料庫 {db_settings['database']} 請求資料")
        cursor.execute(
            searchCommand(
                listFrom="會員資料", 
                key="身分證字號", 
                searchBy = [client.id for client in attendClient_Dict.values()]
            )
        )
        
        print("[*]以下為查詢結果:")
        result = cursor.fetchall()
        
        for idx, item in enumerate(result):
            # <---------- client Processing start ---------->
            if departMode == 1:
                IDhere = item[1]
                client = attendClient_Dict[IDhere]

                client.name = item[0]
                client.birthday = item[2]
                client.foodType = item[4]
                client.specialNeeds = item[5]
                client.nickName = item[6]
            elif departMode == 2:
                IDhere = item[1]
                client = attendClient_Dict[IDhere]

                client.name = item[0]
                client.birthday = item[2]
                client.foodType = item[4]
                client.specialNeeds = item[5]
                client.nickName = item[6]
            # <---------- client Processing end ---------->       

            # <---------- parameters setting start ---------->
            warningFlag = False
            codeExpired = False
            codeHasBeenUsed = False
            yearsOld = year_cal.get_years_old(client.birthday, departDay)
            client.yearsOld = yearsOld
            # <---------- parameters setting end ---------->

            # <---------- cost setting start ---------->
            if yearsOld >=0 and yearsOld <= 3:
                cost = costList[0]
            elif yearsOld >= 4 and yearsOld <= 6:
                cost = costList[1]
            elif yearsOld >= 7 and yearsOld <= 12:
                cost = costList[2]
            elif yearsOld >= 13 and yearsOld <= 64:
                cost = costList[3]
            elif yearsOld >= 65:
                cost = costList[4]
            client.cost = cost
            # <---------- cost setting end ---------->

            # <---------- code checker start ---------->
            if "房" in client.discountCode:
                raise WrongDepartTypeChoose

            if client.discountCode not in  ('NaN', 'nan'):    # 表單有填序號才執行序號有效性判斷
                # <---------- deadline check start ---------->
                deadlineChecker = conn.cursor()
                deadlineChecker.execute(
                    searchCommand(
                        listFrom="旅遊金序號",
                        key="序號",
                        searchBy=client.discountCode
                    )
                )
                codeDeadline = deadlineChecker.fetchall()[0][6].split(".") # codeDeadline = [YYYY, MM, DD]
                departDayL = str(departDay).split("-")                    
                
                if int(departDayL[0]) > int(codeDeadline[0]):
                    codeExpired = True
                elif int(departDayL[1]) > int(codeDeadline[1]):
                    codeExpired = True
                elif int(departDayL[2]) > int(codeDeadline[2]):
                    codeExpired = True

                # <---------- deadline check end ---------->
                if not codeExpired:                
                    cursor.execute(
                        searchCommand(
                            listFrom="旅遊金序號", 
                            key="序號", 
                            searchBy = client.discountCode
                        )
                    )     
                    
                    codeResult = cursor.fetchall()[0]
                    # """"""""""""""""""""""""""""""""""""""""""""""""""""""
                    #                       codeResult
                    # 序號    金額    是否使用過    使用者    使用日期    操作者    使用期限    擁有者    產生日期
                    # """"""""""""""""""""""""""""""""""""""""""""""""""""""
                    code_valid = True if codeResult[2] == 0 else False
                    code_discount = int(codeResult[1]) if code_valid else 0                    
                    
                    if code_valid:
                        codeHasBeenUsed = False
                        originalCost = cost
                        cost -= code_discount
                        client.cost = cost
                        print(f"[!]{item[0]} 兌換了 {code_discount} 元的優惠券!     詳細資訊: {originalCost}元 -> {client.cost}元")              

                        
                        # 序號在有效期限內才執行兌換程序
                        cursor.execute(
                            # 將序號設定為: 已使用
                            editCommand(
                                listFrom='旅遊金序號',
                                searchBy_key='序號',
                                searchBy_value=client.discountCode,
                                key_toUpdate='是否使用過',
                                value_toUpdate=1
                            )
                        )
                        conn.commit()
                        cursor.execute(
                            editCommand(
                                # 更新序號使用者資訊
                                listFrom='旅遊金序號',
                                searchBy_key='序號',
                                searchBy_value=client.discountCode,
                                key_toUpdate='使用者',
                                value_toUpdate=item[0]  # 使用者姓名
                            )
                        )
                        conn.commit()
                        cursor.execute(
                            editCommand(
                                # 更新序號使用日期
                                listFrom='旅遊金序號',
                                searchBy_key='序號',
                                searchBy_value=client.discountCode,
                                key_toUpdate='使用日期',
                                value_toUpdate=str(departDay)
                            )
                        )
                        conn.commit()
                    else:
                        warningFlag = True
                        codeHasBeenUsed = True
                else:
                    warningFlag = True
                    code_valid = False
            else:
                code_valid = False
            # <---------- code checker end ---------->

            # <---------- total travel days start ---------->
            cursor.execute(
                searchCommand(
                    listFrom="會員資料",
                    key="身分證字號",
                    searchBy=item[1]
                )
            )
            d = cursor.fetchall()[0][-1]
            totalTravelDays_now = int(d)
            totalTravelDays_updated = totalTravelDays_now + travelDays
            cursor.execute(
                editCommand(
                    listFrom="會員資料",
                    key_toUpdate="旅遊天數",
                    value_toUpdate=totalTravelDays_updated,
                    searchBy_key="身分證字號",
                    searchBy_value=item[1]
                )
            )
            conn.commit()
            cursor.execute(
                searchCommand(
                    listFrom="會員資料",
                    key="身分證字號",
                    searchBy=item[1]
                )
            )
            # <---------- total travel days end ---------->

            

            client.discountUsed = '是' if code_valid else '否'
            
            if warningFlag:
                client.alertMsg = ""
                if codeHasBeenUsed:
                    client.alertMsg += '序號已被使用過 '
                if codeExpired:
                    client.alertMsg += f'序號已於 {".".join(codeDeadline)} 過期 '

        # <---------- Making xlsx start ---------->
        if departMode == 1:
            df = xlsx_DataFrame(
                clientList = attendClient_Dict.values(),
                mode = "including_roomType"
            )
        elif departMode == 2:
            df = xlsx_DataFrame(
                clientList = attendClient_Dict.values(),
                mode = "excluding_roomType"
            )
        print(df)

        excelName = "出團清冊" + datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + ".xlsx"
        df.to_excel(
            excelName,
            sheet_name= "出團清冊",
            index=False,
            na_rep="空值"
        )
        print("[*]已自動產生 -> " + excelName)
        # <---------- Making xlsx end ---------->

        # <----- Write Operation Log start ----->
        operationTime = datetime.datetime.now()
        operationConfigBasePath = f"{os.getcwd()}\\操作紀錄"
        operationConfigPath = operationConfigBasePath + "\\" + f"{operationTime.strftime('%Y-%m')}月份操作紀錄.ini"    
        if not os.path.isdir(operationConfigBasePath):
            os.mkdir(operationConfigBasePath)
        if not config.check_config_if_exist(operationConfigPath):                
            config.make_config(operationConfigPath, configMode=3)    
        
        operationLog = f"   操作時間: {operationTime}\n   >出團日期: {departDay.strftime('%Y.%M.%D')}\n   出團名單: {tuple([client.name for client in attendClient_Dict.values()])}\n"

        config.write_config(
            path = operationConfigPath,
            content = operationLog
        )
        # <----- Write Operation Log end ----->
    except WrongDepartTypeChoose:
        print("[*]===================================================================================================================================")
        print("[!]警告: 可能在出團模式選擇處選擇錯誤，請確認輸入的Excel表格是否為有包含房型選項的格式，確認後請重新選擇出團模式為「報名表單包含房型選項」")
        print("[*]===================================================================================================================================")
    finally:
        input("[*]請按任意鍵回到 粉鳥旅行社會員資料庫管理系統-功能選擇介面...")

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

def pinkbird_function(functionChoose):
    """
    功能清單
    type functionChoose: str
    """
    clearConsole()
    method = functionDefined.get(functionChoose, default)

    return method()

def default():
    print("請重新選擇功能")

def exit_pinkbird_system():
    try:
        conn.close()
    except NameError:
        # 尚未成功連線就結束程式的狀況
        pass
    print(f"[!]程式結束...  本次執行時間: {datetime.datetime.now()-loginTime}")
    raise Endding

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

def generate_discountCode(codeAmount, randomAmount, codeValue, prefix, clientName, deadline):
    codeGenerator = {}
    for _ in range(codeAmount):
        codeTemp = prefix + ''.join(secrets.choice(string.ascii_letters) for _ in range(randomAmount))
        codeGenerator[codeTemp] = codeValue
    
    code = conn.cursor()
    codeClass = []
    for item in codeGenerator.items():
        nowTime = datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S')
        code.execute(
            f"INSERT INTO `旅遊金序號`(`序號`, `金額`, `是否使用過`, `使用者`, `使用日期`, `操作者`, `使用期限`, `擁有者`, `產生時間`) VALUES ('{str(item[0])}', {int(item[1])}, 0, '', '', '{db_settings['user']}', '{deadline}', '{clientName}', '{nowTime}')"
        )
        conn.commit()
        print(f"[!]序號: {item[0]}   價值: {item[1]}元  產生成功 -> 屬於 {clientName}, 操作者： {db_settings['user']}, 產生時間： {nowTime}")
        codeClass.append(
            Code(
                code = item[0],
                value = item[1],
                clientName = clientName,
                deadline = deadline,
                generateBy = db_settings["user"],
                generateTime = nowTime
            )
        )

    df = pd.DataFrame(
        {
            "序號": [codeItem.code for codeItem in codeClass],
            "金額": [codeItem.value for codeItem in codeClass],
            "姓名": [codeItem.clientName for codeItem in codeClass],
            "使用期限": [codeItem.deadline for codeItem in codeClass],
            "序號發放者": [codeItem.generateBy for codeItem in codeClass],
            "發放時間": [codeItem.generateTime for codeItem in codeClass]
        }
    )
    
    excelName = str(clientName) + "-" + str(datetime.datetime.now().strftime('%Y%m%d-%H%M%S')) + ".xlsx"
    df.to_excel(
        excelName,
        sheet_name= "旅遊金",
        index=False,
    )
    code.close()

def clearConsole() -> None:
    command = "clear"
    if os.name in ("nt", "dos"):  # If Machine is running on Windows, use cls
        command = "cls"
    os.system(command)

def discountCode():
    print('[*]序號產生器說明:')
    print('[*]由序號擁有人之身分證字號數字9碼 + 五位亂數 -> 組合而成')
    print('[*]================模式選擇=================')
    print('[*]          1. 發放折扣碼')
    print('[*]          2. 產生官方折扣碼')
    print('[*]========================================')
    while True:
        try:
            mode = int(input("請選擇功能： "))
            if mode not in (1, 2):
                continue
            break
        except ValueError:
            input("[!]輸入格式有誤，請按「Enter鍵」來重新輸入...")

    
    while True:
        try:
            discountNums = int(input("[?]要產生幾組序號？ "))
            break
        except ValueError:
            input("[!]輸入格式有誤，請按「Enter鍵」來重新輸入...")

    while True:
        try:
            discountValue = int(input('[?]每張折扣碼的價值要設定為多少? '))
            break
        except ValueError:
            input("[!]輸入格式有誤，請按「Enter鍵」來重新輸入...")

    while True:
        try:
            deadline = input("[?]序號有效期限(YYYY.MM.DD)：")
            break
        except ValueError:
            input("[!]輸入格式有誤，請按「Enter鍵」來重新輸入...")
        

    if mode == 2:
        # 產生序號： Pinkbird@@@@@
        generate_discountCode(
            codeAmount = discountNums, 
            randomAmount = 5, 
            codeValue = discountValue, 
            prefix = "Pinkbird",
            clientName = '粉鳥旅行社',
            deadline = deadline
        )
        clientName = '粉鳥旅行社'
    elif mode == 1:
        prefix = input("[?]輸入客人的身分證字號(包含英文字)： ")
        searcher = conn.cursor()
        searcher.execute(
            searchCommand(
                listFrom="會員資料",
                key="身分證字號",
                searchBy=prefix
            )
        )
        clientName = searcher.fetchall()[0][0]
        generate_discountCode(
            codeAmount = discountNums, 
            randomAmount = 5, 
            codeValue = discountValue, 
            prefix = prefix,
            clientName = clientName,
            deadline = deadline
        )

    # <----- Write Operation Log start ----->
    operationTime = datetime.datetime.now()
    operationConfigBasePath = f"{os.getcwd()}\\操作紀錄"
    operationConfigPath = operationConfigBasePath + "\\" + f"{operationTime.strftime('%Y-%m')}月份操作紀錄.ini"    
    if not os.path.isdir(operationConfigBasePath):
        os.mkdir(operationConfigBasePath)
    if not config.check_config_if_exist(operationConfigPath):                
        config.make_config(operationConfigPath, configMode=3)    
    
    operationLog = f"   產生時間: {operationTime}\n   >折扣碼產生者: {db_settings['user']}\n   共產生了 {discountNums} 張 屬於 {clientName} 的 {discountValue} 元的折扣碼\n"

    config.write_config(
        path = operationConfigPath,
        content = operationLog
    )
    # <----- Write Operation Log end ----->

def editClientProfile():
    editor = conn.cursor()
    clientID = input("[?]請輸入要更新資料的會員的身分證字號: ")
    editor.execute(
        searchCommand(
            listFrom="會員資料",
            key="身分證字號",
            searchBy=clientID
        )
    )
    clientData = editor.fetchone()
    try:
        preData = f"姓名: {clientData[0]}    身分證字號: {clientData[1]}    生日: {clientData[2]}   電話: {clientData[3]}   餐食: {clientData[4]}   特殊需求: {clientData[5]}   社群暱稱: {clientData[6]}"
    except TypeError:
        print("[!]資料庫中無此 身分證字號 對應之資料")
        return
    print("[*]======================================================客戶目前資料=======================================================")    
    print("[>]" + preData)
    print("[*]========================================================================================================================")
    print("[*]如果只是要查詢會員資料請在確認完會員資料後輸入「e」即可")
    print("[*]可編輯選項: 1.姓名    2.身分證字號    3.生日    4.電話    5.餐食    6.特殊需求    7.社群暱稱    delete: 刪除此筆會員資料    e: 取消")
    editMode_Dict = {
        "1": "姓名",
        "2": "身分證字號",
        "3": "生日",
        "4": "電話",
        "5": "餐食",
        "6": "特殊需求",
        "7": "社群暱稱"
    }

    while True:
        editMode = input("[?]請選擇要編輯的項目: ")
        if editMode in ("e", "E"):
            print("[!]已取消編輯...")
            return 0
        elif editMode in ('1', '2', '3', '4', '5', '6', '7', 'delete'):
            break
        else:
            print("[!]請重新輸入 \"編輯選項\" 中的選項...")
            continue
    
    if editMode == "delete":
        while True:
            deleteCheck = input(f"[!]確定要刪除 {clientID} 的會員資料嗎(Y/N)? ")
            if deleteCheck in ('y', 'Y'):
                editor.execute(
                    deleteCommand(
                        listFrom='會員資料',
                        key="身分證字號",
                        value=clientID
                    )
                )
                conn.commit()
                print(f"[*]已刪除 {clientID} 的會員資料")
                break
            elif deleteCheck in ('n', 'N'):
                print(f"[!]已取消刪除 {clientID} 的會員資料")            
                return 0
    else:    
        newValue = input(f"[?]請問要將 {editMode_Dict[editMode]} 改為(請輸入數值)? ")

        editor.execute(
            editCommand(
                listFrom="會員資料",
                key_toUpdate=editMode_Dict[editMode],
                value_toUpdate=newValue,
                searchBy_key="身分證字號",
                searchBy_value=clientID
            )
        )
        conn.commit()
        
        if editMode == '2':
            clientID = newValue

        editor.execute(
            searchCommand(
                listFrom="會員資料",
                key="身分證字號",
                searchBy=clientID
            )
        )
        clientDataNew = editor.fetchone()
        print("[*]======================================================更新後的資料=======================================================")
        output = f"姓名: {clientDataNew[0]}    身分證字號: {clientDataNew[1]}    生日: {clientDataNew[2]}   電話: {clientDataNew[3]}   餐食: {clientDataNew[4]}   特殊需求: {clientDataNew[5]}   社群暱稱: {clientDataNew[6]}"
        print("[>]" + output)
        print("[*]========================================================================================================================")

    # <----- Write Operation Log start ----->
    operationConfigBasePath = f"{os.getcwd()}\\操作紀錄"
    operationTime = datetime.datetime.now()
    operationConfigPath = operationConfigBasePath + "\\" + f"{operationTime.strftime('%Y-%m')}月份操作紀錄.ini"
    
    if not os.path.isdir(operationConfigBasePath):
        os.mkdir(operationConfigBasePath)
    if not config.check_config_if_exist(operationConfigPath):                
        config.make_config(operationConfigPath, configMode=3)

    if editMode != "delete":
        operationLog = f"   編輯時間: {operationTime}\n   >編輯前資料:\n   {preData}\n"

        config.write_config(
            path = operationConfigPath,
            content = operationLog
        )

        operationLog = f"   >編輯後資料:\n   {output}\n"
        config.write_config(
            path = operationConfigPath,
            content = operationLog
        )
    elif editMode == 'delete':
        operationLog = f"   編輯時間: {operationTime}\n   >刪除了 {clientID} 的會員資料\n"

        config.write_config(
            path = operationConfigPath,
            content = operationLog
        )
    # <----- Write Operation Log end ----->

def addClientProfile():
    addClient = Client()
    addClient.name = input("[?]請輸入 客戶姓名: ")
    addClient.id = input("[?]請輸入 身分證字號: ")
    addClient.birthday = input("[?]請輸入 出生年月日: ")
    addClient.phone = input("[?]請輸入 連絡電話: ")
    addClient.foodType = input("[?]請輸入 餐食選項: ")
    addClient.specialNeeds = input("[?]請輸入 特殊需求: ")
    addClient.nickName = input("[?]請輸入 社群暱稱: ")
    addClient.travelDays = 0
    
    editor = conn.cursor()
    editor.execute(
        insertCommand(
            listFrom = "會員資料",
            key = ('姓名', '身分證字號', '生日', '電話', '餐食', '特殊需求', '暱稱', '旅遊天數'),
            value = (
                addClient.name,
                addClient.id,
                addClient.birthday,
                addClient.phone,
                addClient.foodType,
                addClient.specialNeeds,
                addClient.nickName,
                addClient.travelDays
            )
        )
    )
    conn.commit()
    editor.execute(
        searchCommand(
            listFrom="會員資料",
            key = '身分證字號',
            searchBy=addClient.id
        )
    )
    newData = editor.fetchall()[0]
    print("[*]======================================================新增客戶資料=======================================================")
    printData = f"姓名: {newData[0]}    身分證字號: {newData[1]}    生日: {newData[2]}   電話: {newData[3]}   餐食: {newData[4]}   特殊需求: {newData[5]}   社群暱稱: {newData[6]}"
    print("[>]" + printData)
    print("[*]========================================================================================================================")
    # <----- Write Operation Log start ----->
    operationConfigBasePath = f"{os.getcwd()}\\操作紀錄"
    operationTime = datetime.datetime.now()
    operationConfigPath = operationConfigBasePath + "\\" + f"{operationTime.strftime('%Y-%m')}月份操作紀錄.ini"
    
    if not os.path.isdir(operationConfigBasePath):
        os.mkdir(operationConfigBasePath)
    if not config.check_config_if_exist(operationConfigPath):                
        config.make_config(operationConfigPath, configMode=3)

    
    operationLog = f"   新增時間: {operationTime}\n   >新增資料:\n   {printData}\n"

    config.write_config(
        path = operationConfigPath,
        content = operationLog
    )
    # <----- Write Operation Log end ----->

def dataRepeatCheck():
    repeateID_Dict = {}
    selectedList = []
    repeateChecker = conn.cursor()
    reader = conn.cursor()
    repeateChecker.execute(
        "select * from `會員資料` group by `身分證字號` having count(*) > 1"
    )
    response = repeateChecker.fetchall()
    if len(response) == 0:
        print("[!]會員資料庫目前無重複資料")
        return
    while True:
        print("[*]以下為重複會員資料之名單::")
        for clientRepeat in response:
            print(f"[>]姓名: {clientRepeat[0]} 身分證字號: {clientRepeat[1]}")
        input("[*]請按 Enter鍵 開始選擇保留版本")
        clearConsole()

        # <----- choosing start ----->
        for clientRepeat in response:
            print(f"[>]姓名: {clientRepeat[0]} 身分證字號: {clientRepeat[1]}")
            reader.execute(
                searchCommand(
                    listFrom='會員資料',
                    key='身分證字號',
                    searchBy=clientRepeat[1]
                )
            )
            print(f"[*]以下為 {clientRepeat[1]} {clientRepeat[0]} 的每組重複之資料:")
            for idx, searchResult in enumerate(reader.fetchall()):
                repeateID_Dict[idx+1] = Client()
                repeateID_Dict[idx+1].name = searchResult[0]
                repeateID_Dict[idx+1].id = searchResult[1]
                repeateID_Dict[idx+1].birthday = searchResult[2]
                repeateID_Dict[idx+1].phone = searchResult[3]
                repeateID_Dict[idx+1].foodType = searchResult[4]
                repeateID_Dict[idx+1].specialNeeds = searchResult[5]
                repeateID_Dict[idx+1].nickName = searchResult[6]
                repeateID_Dict[idx+1].travelDays = searchResult[7]
                print(f"[>]{idx+1}. 姓名: {repeateID_Dict[idx+1].name}\t身分證字號: {repeateID_Dict[idx+1].id}\t生日: {repeateID_Dict[idx+1].birthday}\t電話: {repeateID_Dict[idx+1].phone}\t餐食: {repeateID_Dict[idx+1].foodType}\t特殊需求: {repeateID_Dict[idx+1].specialNeeds}\t暱稱: {repeateID_Dict[idx+1].nickName}\t旅遊天數: {repeateID_Dict[idx+1].travelDays}")
            selectFromRepeat = int(input("[?]請從以上重複的資料當中，選擇一筆要保存的資料(輸入編號): "))    # reference: repeateID_Dict[ idx+1 ]
            temp = repeateID_Dict[selectFromRepeat]
            selectedList.append(temp)
            print(f"[*]\t保存的版本:\n[*]\t{selectFromRepeat}. 姓名: {temp.name}\t身分證字號: {temp.id}\t生日: {temp.birthday}\t電話: {temp.phone}\t餐食: {temp.foodType}\t特殊需求: {temp.specialNeeds}\t暱稱: {temp.nickName}\t旅遊天數: {temp.travelDays}")
            print("[-]")
            input("[*]請按 Enter鍵 繼續選取...")
            print("[-]")
        clearConsole()
        print("[*]以下為最終選取的保留版本:")
        for selected in selectedList:
            print(f"[*]姓名: {selected.name}\t身分證字號: {selected.id}\t生日: {selected.birthday}\t電話: {selected.phone}\t餐食: {selected.foodType}\t特殊需求: {selected.specialNeeds}\t暱稱: {selected.nickName}\t旅遊天數: {selected.travelDays}")
        reChoose = input("[*]如果要重新選擇，請輸入「re」，如果確認要使用上述資料作為最新資料，直接按「Enter鍵」即可繼續")
        if reChoose != "re":            
            break
        selectedList = []
        clearConsole()
        # <----- choosing end ----->    

    finalCheck_BeforeEdit = input("[?]是否確定要更新資料(y/n): ")
    if finalCheck_BeforeEdit in ('y, "Y'):        
        for client in selectedList:
            # DELETE
            repeateChecker.execute(
                deleteCommand(
                    listFrom="會員資料",
                    key="身分證字號",
                    value=client.id
                )
            )
            conn.commit()
            # re:ADD
            repeateChecker.execute(
                insertCommand(
                    listFrom="會員資料",
                    key = ('姓名', '身分證字號', '生日', '電話', '餐食', '特殊需求', '暱稱', '旅遊天數'),
                    value = (
                        client.name,
                        client.id,
                        client.birthday,
                        client.phone,
                        client.foodType,
                        client.specialNeeds,
                        client.nickName,
                        client.travelDays
                    )
                )
            )
            conn.commit()
            print(f"[*]{client.name} 資料已更新 ")
        repeateChecker.execute(
            "SELECT `身分證字號` FROM `會員資料` WHERE 1"
        )
        print(f"[*]所有資料庫中重複的資料已更新完成 目前資料庫總共有: {len(repeateChecker.fetchall())} 筆資料")
    elif finalCheck_BeforeEdit in ('n', 'N'):
        print("[*]已取消更新")
    # <----- Write Operation Log start ----->
    operationConfigBasePath = f"{os.getcwd()}\\操作紀錄"
    operationTime = datetime.datetime.now()
    operationConfigPath = operationConfigBasePath + "\\" + f"{operationTime.strftime('%Y-%m')}月份操作紀錄.ini"
    
    if not os.path.isdir(operationConfigBasePath):
        os.mkdir(operationConfigBasePath)
    if not config.check_config_if_exist(operationConfigPath):                
        config.make_config(operationConfigPath, configMode=3)

    
    operationLog = f"   操作時間: {operationTime}\n   >更動名單:\n   {[client.name for client in selectedList]}\n"

    config.write_config(
        path = operationConfigPath,
        content = operationLog
    )
    # <----- Write Operation Log end ----->


functionDefined = {
    "1": registeForm_processing,
    "2": discountCode,
    "3": editClientProfile,
    "4": addClientProfile,
    "5": dataRepeatCheck,
    "E": exit_pinkbird_system,
    "e": exit_pinkbird_system
}

if __name__ == '__main__':
    # <----- System setting config start ----->
    if not config.check_config_if_exist(path=f"{os.getcwd()}\\config.ini"):
        print("[!]警告: 系統找不到 config.ini")
        print(f"[/]自動產生 config.ini 中...")

        configPath = f"{os.getcwd()}\\config.ini"
        config.make_config(configPath, configMode=1)

        print(f"[*]config.ini 產生成功 -> 檔案路徑: {configPath}")
        print("[!]訊息: 請在完成設定 config.ini 後再重新開啟程式")
        os.system('pause')
        sys.exit()
    configResult = config.load_config(path = "./config.ini")
    # <----- System setting config end ----->

    print("[*]========================================")
    print("[*]" + "粉鳥旅行社會員資料庫管理系統".center(25))
    print("[*]" + programVersion.center(35))
    print("[*]========================================")
    retryLoginCount = 0      
    while True:
        global db_settings
        # 資料庫參數設定
        db_settings = {
            "host": configResult["host"],
            "port": int(configResult["port"]),
            "user": input('[?]帳號: '),
            # "user": "root",
            "password": input('[?]密碼: '),
            # "password": "Cyuanz-0126",
            "database": "pinkbird",
            "charset": "utf8"
        }
        print("[*]========================================")
        try:
            global conn
            print(f"[-]連接至資料庫 -> {db_settings['database']} 中, 路徑為: {db_settings['host']}:{db_settings['port']}")            
            loginTime = datetime.datetime.now()
            conn = pymysql.connect(**db_settings)            
            clearConsole()
            print(f"[*]資料庫: {db_settings['database']} 連線成功!")
            loginSuccess = True            
            break
        except pymysql.err.OperationalError:            
            print(f"[!]第 {retryLoginCount+1} 次嘗試登入失敗")
            if retryLoginCount > 0:
                print("[*](看到這段訊息代表你嘗試登入失敗一次以上)如果確認帳號密碼輸入無錯誤，可能是網路連線上的設定問題，請連絡相關人員設定")                
            retryLogin = input('[!]帳號或密碼有錯，請問是否要重新輸入，否則系統自動關閉(Y/N): ')            
            loginSuccess = False
            if retryLogin in ('y', 'Y'):
                retryLoginCount += 1                
                continue
            else:
                exit_pinkbird_system()
        finally:
            # <----- Write Login Log start ----->
            configBasePath = f"{os.getcwd()}\\登入紀錄"
            configPath = configBasePath + "\\" + f"{loginTime.strftime('%Y-%m')}月份-登入紀錄.ini"
            if not os.path.isdir(configBasePath):
                os.mkdir(configBasePath)

            if not config.check_config_if_exist(configPath):                
                config.make_config(configPath, configMode=2)

            if loginSuccess:
                loginLog = f"{loginTime}\t{db_settings['user']}\t{'登入成功'}\n"
            else:
                loginLog = f"{loginTime}\t{db_settings['user']}\t{'登入失敗'}\n"

            config.write_config(
                path = configPath,
                content = loginLog
            )
            # <----- Write Login Log end ----->
    # <----- Main Loop start ----->
    while True:
        print("[*]========================================")
        print("[*]" + "粉鳥旅行社會員資料庫管理系統".center(25))
        print("[*]" + programVersion.center(35))
        print("[*]========================================")
        print(f'[*]目前登入身分為: {db_settings["user"]}')        
        print(f'[*]登入時間為: {loginTime.strftime("%Y-%m-%d_%H:%M:%S")}')
        print("[*]" + "================功能選項================")   
        print("[*]" + "\t  1. 產生出團名冊")
        print("[*]" + "\t  2. 產生折扣碼") 
        print("[*]" + "\t  3. 編輯或查詢會員資料") 
        print("[*]" + "\t  4. 手動新增會員資料")
        print("[*]" + "\t  5. 檢查會員資料是否重複")
        print("[*]" + "\t  e. 離開系統")
        print("[*]" + "="*40)
        print("[*]在各功能介面中，隨時可以按下「Ctrl + C」回到此主選單介面")
        functionChoose = input(f"[?]請選擇功能: ")
        
        if functionChoose not in functionDefined:
            print("[*]===============================================")
            print("[?]請重新輸入功能選單中之數字...")
            os.system("pause")
            continue

        try:
            # <----- Write Operation Log start ----->
            operationTime = datetime.datetime.now()
            operationConfigBasePath = f"{os.getcwd()}\\操作紀錄"
            operationConfigPath = operationConfigBasePath + "\\" + f"{operationTime.strftime('%Y-%m')}月份操作紀錄.ini"
            if not os.path.isdir(operationConfigBasePath):
                os.mkdir(operationConfigBasePath)

            if not config.check_config_if_exist(operationConfigPath):                
                config.make_config(operationConfigPath, configMode=3)

            if functionChoose == "1":
                operationName_inChinese = "產生出團名冊"
            elif functionChoose == "2":
                operationName_inChinese = "產生折扣碼"
            elif functionChoose == "3":
                operationName_inChinese = "編輯會員資料"
            elif functionChoose == "4":
                operationName_inChinese = "手動新增會員資料"
            elif functionChoose == "5":
                operationName_inChinese = "檢查會員資料是否重複"
            elif functionChoose in ('e', 'E'):
                operationName_inChinese = "結束系統"
            
            operationLog = f"{operationTime}\t{db_settings['user']}\t{operationName_inChinese}\n"

            config.write_config(
                path = operationConfigPath,
                content = operationLog
            )
            # <----- Write Operation Log end ----->

            pinkbird_function(functionChoose)            
        except Endding:
            pass
        except KeyboardInterrupt:
            print("\n[*]系統將回到主選單")
        finally:
            os.system("pause")

            # 結束每階段任務後清除 Console
            clearConsole()
    # <----- Main Loop end ----->
