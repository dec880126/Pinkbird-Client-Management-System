"""
PINKBIRD CLIENT DATABASE SYSTEM
Copyright (c) 2021 CyuanHuang
FUNCTION LIST:

 - Departure clients' infomation list generator
 - Discount code generator
 - Clients' profile editor
 - Add NEW Clients' profile
 - Check if the data has duplicated in the database
 - Open phpMyAdmin in default web browser
 - Overview and analysis of database

ALL OF THE FUNCTION PROVIDED ARE WORKING BASE ON SQL(Structured Query Language)
"""
# ? Modules
import pandas as pd
import pymysql
import datetime
from rich.progress import track
import sys
import os
import string
import secrets
import webbrowser


# ? Packages
import package.year_cal as year_cal
import package.config as config
from package.sql_command import searchCommand, deleteCommand, insertCommand, editCommand, countCommand, searchCommand_sp
from package.tools import set_cost, clearConsole, xlsx_DataFrame, default

programVersion = "版本: " + "5.3.0"

class Client:
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
        # 2021.09.01 update
        self.seat = "無"
        self.disability = "無"

class Code:
    def __init__(
        self, code, value, clientName, deadline, generateBy, generateTime
    ) -> None:
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
    pass

class Illegal_discountCode(Exception):
    pass


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
            break
        else:
            print("[!]請重新輸入正確的選項....")
            os.system("pause")
    mode_inChinese = "「不」包含房型選項" if departMode == 1 else "包含房型選項"
    print(f"[*]目前模式: {departMode}. {mode_inChinese}")
    # <---------- departMode selecting end ---------->

    # <---------- reading xlsx start ---------->
    filePath = input("[?]請將檔案拉到程式畫面中...")
    try:
        if departMode == 1:
            try:
                # 2021.09.01 fixed
                # ValueError: Worksheet named '表單回應 1' not found
                df = pd.read_excel(
                    filePath,
                    sheet_name="表單回應 1",
                    usecols="B:G",  # B:G順序為: "身分證字號", "連絡電話", "上車地點", "身心障礙手冊", "序號", "座位"
                )
            except ValueError:
                df = pd.read_excel(
                    filePath,
                    sheet_name="Form Responses 1",
                    usecols="B:G",  # B:G順序為: "身分證字號", "連絡電話", "上車地點", "身心障礙手冊", "序號", "座位"
                )
        elif departMode == 2:
            try:
                df = pd.read_excel(
                    filePath,
                    sheet_name="表單回應 1",
                    usecols="B:I",  # B:I順序為: "身分證字號", "連絡電話", "上車地點", "房型", "同房者", "身心障礙手冊", "序號", "座位"
                )
            except ValueError:
                df = pd.read_excel(
                    filePath,
                    sheet_name="Form Responses 1",
                    usecols="B:I",  # B:I順序為: "身分證字號", "連絡電話", "上車地點", "房型", "同房者", "身心障礙手冊", "序號", "座位"
                )
        # print(df)
    except OSError:
        clearConsole()
        print(
            "[*]========================================================================================"
        )
        print("[!]警告: 由於 Windows 系統不支援檔案名稱中有空格的程式操作 請將檔案名稱中的空格刪除後再重新執行")
        print(
            "[*]========================================================================================"
        )
        print("[*]幫助: 範例: 粉鳥旅行社多日遊報名表單範例 (回覆).xlsx    <- 此為檔案名稱")
        print("[*]           通常空格存在於「(回覆)」的前面，刪除空格後程式即可正常執行!")
        print("[!]提醒: 空格的原因是因為 Google 端的設定，所以在匯入前要特別留意")
        print(
            "[*]========================================================================================"
        )
        input("[*]請按任意鍵回到 粉鳥旅行社會員資料庫管理系統-功能選擇介面...")
        return
    # <---------- reading xlsx end ---------->

    # <---------- depart info start ---------->
    while True:
        departDay_raw = input("[?]請輸入出團日期(YYYY.MM.DD)： ").split(".")

        try:
            departDay = datetime.date(
                year=int(departDay_raw[0]),
                month=int(departDay_raw[1]),
                day=int(departDay_raw[2]),
            )
            if datetime.date.today() > departDay:
                print("[!]提醒: 出團日期不能不能為過去!") # 2021.09.01 update
                continue
            break
        except IndexError:
            print("[!]日期輸入格式錯誤，請重新輸入，並確認格式為: YYYY.MM.DD")
        except ValueError:
            print("[!]日期輸入格式錯誤，請重新輸入，並確認格式為: YYYY.MM.DD")

    while True:
        try:
            travelDays = int(input("[?]此次出團為幾日團(輸入數字)? "))
            break
        except ValueError:
            print("[!]輸入格式錯誤，請重新輸入，並確認格式為純數字")

    costList = set_cost()
    # <---------- depart date info end ---------->

    # <---------- client class processing start ---------->
    # registerForm_List = []  # 報名表單的客戶清單 -> class
    attendClient_Dict = {}  # 參加的客戶清單 -> class

    if departMode == 1:
        for idx in range(df.shape[0]):
            IDhere = df.at[idx, df.columns[0]]
            attendClient_Dict[IDhere] = Client()

            # 順序為: "身分證字號", "連絡電話", "上車地點", "身心障礙手冊", "序號", "座位"
            attendClient_Dict[IDhere].id = IDhere
            attendClient_Dict[IDhere].phone = df.at[idx, df.columns[1]]
            attendClient_Dict[IDhere].location = df.at[idx, df.columns[2]]
            attendClient_Dict[IDhere].disability = str(df.at[idx, df.columns[3]])
            attendClient_Dict[IDhere].discountCode = str(df.at[idx, df.columns[4]])            
            attendClient_Dict[IDhere].seat = df.at[idx, df.columns[5]]
            attendClient_Dict[IDhere].roomType = None
            attendClient_Dict[IDhere].roommate = None
            

            # 測試讀取錯誤的狀況 如果出正常則continue，否則系統將顯示提醒訊息
            # print(attendClient_Dict[IDhere].disability)
            if "是" in attendClient_Dict[IDhere].disability or "否" in attendClient_Dict[IDhere].disability:
                continue

            print("[!]可能是出團表單中包含房型選項，請重新選擇出團模式")
            raise KeyboardInterrupt
    elif departMode == 2:
        for idx in range(df.shape[0]):
            IDhere = df.at[idx, df.columns[0]]
            attendClient_Dict[IDhere] = Client()

            # 順序為: "身分證字號", "連絡電話", "上車地點", "房型", "同房者", "身心障礙手冊", "序號", "座位"
            attendClient_Dict[IDhere].id = IDhere
            attendClient_Dict[IDhere].phone = df.at[idx, df.columns[1]]
            attendClient_Dict[IDhere].location = df.at[idx, df.columns[2]]
            attendClient_Dict[IDhere].roomType = df.at[idx, df.columns[3]]
            attendClient_Dict[IDhere].roommate = df.at[idx, df.columns[4]]
            attendClient_Dict[IDhere].disability = df.at[idx, df.columns[5]]
            attendClient_Dict[IDhere].discountCode = str(df.at[idx, df.columns[6]])
            attendClient_Dict[IDhere].seat = df.at[idx, df.columns[7]]
    # <---------- client class processing end ---------->

    try:
        cursor = conn.cursor()
        print(f"[-]正在向資料庫 {db_settings['database']} 請求資料")
        cursor.execute(
            searchCommand(
                listFrom="會員資料",
                key="身分證字號",
                searchBy=[client.id for client in attendClient_Dict.values()],
            )
        )

        print("[*]以下為查詢結果:")
        result = cursor.fetchall()

        for step, item in zip(track(result, description="[\]處理中"), result):
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
            if yearsOld >= 0 and yearsOld <= 3:
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

            if client.discountCode not in ("NaN", "nan"):  # 表單有填序號才執行序號有效性判斷
                try:
                    code_exist = True
                    # <---------- deadline check start ---------->
                    deadlineChecker = conn.cursor()
                    deadlineChecker.execute(
                        f"SELECT `使用期限` FROM `旅遊金序號` WHERE `序號` = '{client.discountCode}'"
                    )
                    codeDeadline = deadlineChecker.fetchone()

                    #     File "Y:\python\PCMS\PCMS.py", line 302, in registeForm_processing
                    #         if type(codeDeadline[0]) is None:
                    # TypeError: 'NoneType' object is not subscriptable
                    try:
                        illegal = False
                        codeDeadline = codeDeadline[0].split(".")  # codeDeadline = [YYYY, MM, DD]
                    except TypeError:
                        illegal = True

                    if illegal:
                        raise Illegal_discountCode
                    # departDayL = str(departDay).split("-")

                    codeDeadline = datetime.date(
                        year=int(codeDeadline[0]),
                        month=int(codeDeadline[1]),
                        day=int(codeDeadline[2]),
                    )

                    if departDay > codeDeadline:
                        codeExpired = True

                    # if int(departDayL[0]) > int(codeDeadline[0]):
                    #     codeExpired = True
                    # elif int(departDayL[1]) > int(codeDeadline[1]):
                    #     codeExpired = True
                    # elif int(departDayL[2]) > int(codeDeadline[2]):
                    #     codeExpired = True

                    # <---------- deadline check end ---------->
                    if not codeExpired:
                        cursor.execute(
                            searchCommand(
                                listFrom="旅遊金序號", key="序號", searchBy=client.discountCode
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
                            print(
                                f"[!]{item[0]} 兌換了 {code_discount} 元的優惠券!     詳細資訊: {originalCost}元 -> {client.cost}元"
                            )

                            # 序號在有效期限內才執行兌換程序
                            cursor.execute(
                                # 將序號設定為: 已使用
                                editCommand(
                                    listFrom="旅遊金序號",
                                    searchBy_key="序號",
                                    searchBy_value=client.discountCode,
                                    key_toUpdate="是否使用過",
                                    value_toUpdate=1,
                                )
                            )
                            conn.commit()
                            cursor.execute(
                                editCommand(
                                    # 更新序號使用者資訊
                                    listFrom="旅遊金序號",
                                    searchBy_key="序號",
                                    searchBy_value=client.discountCode,
                                    key_toUpdate="使用者",
                                    value_toUpdate=item[0],  # 使用者姓名
                                )
                            )
                            conn.commit()
                            cursor.execute(
                                editCommand(
                                    # 更新序號使用日期
                                    listFrom="旅遊金序號",
                                    searchBy_key="序號",
                                    searchBy_value=client.discountCode,
                                    key_toUpdate="使用日期",
                                    value_toUpdate=str(departDay),
                                )
                            )
                            conn.commit()
                        else:
                            warningFlag = True
                            codeHasBeenUsed = True
                    else:
                        warningFlag = True
                        code_valid = False
                except IndexError:
                    print(f"[!]{client.name} 的序號 {client.discountCode} 於資料庫中查無資料，詳細資訊可至資料庫中查詢。")
                    warningFlag = True
                    code_valid = False
                    code_exist = False
                except Illegal_discountCode: 
                    print(f"[!]{client.name} 的序號 {client.discountCode} 於資料庫中查無資料，詳細資訊可至資料庫中查詢。")
                    warningFlag = True
                    code_valid = False
                    code_exist = False
            else:
                code_valid = False
            # <---------- code checker end ---------->

            # <---------- total travel days start ---------->
            cursor.execute(
                # 2021.09.01 update
                f"SELECT `旅遊天數` FROM `會員資料` WHERE `身分證字號` = '{item[1]}'"
                # searchCommand(listFrom="會員資料", key="身分證字號", searchBy=item[1])
            )
            d = cursor.fetchone()
            totalTravelDays_updated = int(d[0]) + travelDays
            cursor.execute(
                editCommand(
                    listFrom="會員資料",
                    key_toUpdate="旅遊天數",
                    value_toUpdate=totalTravelDays_updated,
                    searchBy_key="身分證字號",
                    searchBy_value=item[1],
                )
            )
            conn.commit()
            cursor.execute(
                searchCommand(listFrom="會員資料", key="身分證字號", searchBy=item[1])
            )
            # <---------- total travel days end ---------->

            client.discountUsed = "是" if code_valid else "否"

            if warningFlag:
                client.alertMsg = ""
                if codeHasBeenUsed:
                    client.alertMsg += "序號已被使用過 "
                if codeExpired:
                    client.alertMsg += f'序號已於 {".".join(codeDeadline)} 過期 '
                if not code_exist:
                    client.alertMsg += f'序號: {client.discountCode} 不存在 '

        # <---------- Making xlsx start ---------->
        if departMode == 1:
            df = xlsx_DataFrame(
                clientList=attendClient_Dict.values(), mode="excluding_roomType"
            )
        elif departMode == 2:
            df = xlsx_DataFrame(
                clientList=attendClient_Dict.values(), mode="including_roomType"
            )
        print("======================================================================")
        print(df)
        print("======================================================================")

        excelName = "出團清冊" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".xlsx"
        df.to_excel(excelName, sheet_name="出團清冊", index=False, na_rep="空值")
        print("[*]已自動產生 -> " + excelName)
        # <---------- Making xlsx end ---------->

        # <----- Write Operation Log start ----->
        operationTime = datetime.datetime.now()
        operationConfigBasePath = f"{os.getcwd()}\\操作紀錄"
        operationConfigPath = (
            operationConfigBasePath
            + "\\"
            + f"{operationTime.strftime('%Y-%m')}月份操作紀錄.ini"
        )
        if not os.path.isdir(operationConfigBasePath):
            os.mkdir(operationConfigBasePath)
        if not config.check_config_if_exist(operationConfigPath):
            config.make_config(operationConfigPath, configMode=3)

        operationLog = f"   操作時間: {operationTime}\n   >出團日期: {departDay.strftime('%Y.%M.%D')}\n   出團名單: {tuple([client.name for client in attendClient_Dict.values()])}\n"

        config.write_config(path=operationConfigPath, content=operationLog)
        # <----- Write Operation Log end ----->
    except WrongDepartTypeChoose:
        print("[*]===================================================================================================================================")
        print("[!]警告: 可能在出團模式選擇處選擇錯誤，請確認輸入的Excel表格是否為有包含房型選項的格式，確認後請重新選擇出團模式為「報名表單包含房型選項」")
        print("[*]===================================================================================================================================")
    finally: 
        input("[*]請按任意鍵回到 粉鳥旅行社會員資料庫管理系統-功能選擇介面...")


def generate_discountCode(codeAmount, randomAmount, codeValue, prefix, clientName, deadline):
    code = conn.cursor()
    codeClass = {}

    for _ in range(codeAmount):
        while True:
            # <----- 亂碼產生 start ----->
            codeKey = prefix + "".join(
                secrets.choice(string.ascii_letters) for _ in range(randomAmount)
            )
            # <----- 亂碼產生 end ----->

            # <----- 保證產生的序號永不重複 start ----->
            code.execute(
                searchCommand(
                    listFrom="旅遊金序號",
                    key="序號",
                    searchBy=codeKey
                )
            )
            if len(code.fetchall()) != 0:
                continue
            # <----- 保證產生的序號永不重複 end ----->

            # <----- 序號寫入 start ----->
            nowTime = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")
            codeClass[codeKey] = Code(
                code=codeKey,
                value=codeValue,
                clientName=clientName,
                deadline=deadline,
                generateBy=db_settings["user"],
                generateTime=nowTime,
            )
            codeHere = codeClass[codeKey]
            code.execute(
                insertCommand(
                    listFrom="旅遊金序號",
                    key = (
                        "序號", 
                        "金額", 
                        "是否使用過", 
                        "使用者", 
                        "使用日期", 
                        "操作者", 
                        "使用期限", 
                        "擁有者", 
                        "產生時間"
                    ),
                    value = (
                        codeHere.code,
                        codeHere.value,
                        0, "", "",
                        db_settings['user'],
                        codeHere.deadline,
                        codeHere.clientName,
                        codeHere.generateTime
                    )
                )
            )
            conn.commit()
            print(
                f"[!]序號: {codeHere.code}   價值: {codeHere.value}元  產生成功 -> 屬於 {codeHere.clientName}, 操作者： {db_settings['user']}, 產生時間： {codeHere.generateTime}"
            )
            # <----- 序號寫入 end ----->
            break

    df = pd.DataFrame(
        {
            "序號": [codeItem.code for codeItem in codeClass.values()],
            "金額": [codeItem.value for codeItem in codeClass.values()],
            "姓名": [codeItem.clientName for codeItem in codeClass.values()],
            "使用期限": [codeItem.deadline for codeItem in codeClass.values()],
            "序號發放者": [codeItem.generateBy for codeItem in codeClass.values()],
            "發放時間": [codeItem.generateTime for codeItem in codeClass.values()],
        }
    )

    excelName = (
        str(clientName)
        + "-"
        + str(datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
        + ".xlsx"
    )
    df.to_excel(
        excelName,
        sheet_name="旅遊金",
        index=False,
    )
    code.close()


def discountCode():
    print("[*]===============================================")
    print("[*]序號產生器說明:")
    print("[*]由序號擁有人之身分證字號數字9碼 + 五位亂數 -> 組合而成")
    print("[*]================模式選擇=================")
    print("[*]          1. 發放折扣碼")
    print("[*]          2. 產生官方折扣碼")
    print("[*]========================================")
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
            discountValue = int(input("[?]每張折扣碼的價值要設定為多少? "))
            break
        except ValueError:
            input("[!]輸入格式有誤，請按「Enter鍵」來重新輸入...")

    while True:
        deadline_raw = input("[?]序號有效期限(YYYY.MM.DD)： ").split(".")

        try:
            deadline = datetime.date(
                year=int(deadline_raw[0]),
                month=int(deadline_raw[1]),
                day=int(deadline_raw[2]),
            ).strftime("%Y.%m.%d")
            break
        except IndexError:
            print("[!]日期輸入格式錯誤，請重新輸入，並確認格式為: YYYY.MM.DD")
        except ValueError:
            print("[!]日期輸入格式錯誤，請重新輸入，並確認格式為: YYYY.MM.DD")


    while True:
        if mode == 2:
            # 產生序號： Pinkbird@@@@@
            generate_discountCode(
                codeAmount=discountNums,
                randomAmount=5,
                codeValue=discountValue,
                prefix="Pinkbird",
                clientName="粉鳥旅行社",
                deadline=deadline,
            )
            clientName = "粉鳥旅行社"
            break
        elif mode == 1:
            # 產生序號： 123456789@@@@@
            prefix = input("[?]輸入客人的身分證字號(包含英文字)： ")
            searcher = conn.cursor()
            searcher.execute(searchCommand(listFrom="會員資料", key="身分證字號", searchBy=prefix))
            try:
                clientName = searcher.fetchall()[0][0]
            except IndexError:
                print("[!]警告: 輸入的會員身分證字號不在資料庫中，請檢察拼字是否正確。")
                if input("[*]如要繼續產生，可以以官方折扣碼形式產生，請問要繼續執行嗎(y/n)?") in ("y", "Y"):
                    mode = 2
                    continue
                else:
                    return
            generate_discountCode(
                codeAmount=discountNums,
                randomAmount=5,
                codeValue=discountValue,
                prefix=prefix[1:],
                clientName=clientName,
                deadline=deadline,
            )
            break

    # <----- Write Operation Log start ----->
    operationTime = datetime.datetime.now()
    operationConfigBasePath = f"{os.getcwd()}\\操作紀錄"
    operationConfigPath = (
        operationConfigBasePath + "\\" + f"{operationTime.strftime('%Y-%m')}月份操作紀錄.ini"
    )
    if not os.path.isdir(operationConfigBasePath):
        os.mkdir(operationConfigBasePath)
    if not config.check_config_if_exist(operationConfigPath):
        config.make_config(operationConfigPath, configMode=3)

    operationLog = f"   產生時間: {operationTime}\n   >折扣碼產生者: {db_settings['user']}\n   共產生了 {discountNums} 張 屬於 {clientName} 的 {discountValue} 元的折扣碼\n"

    config.write_config(path=operationConfigPath, content=operationLog)
    # <----- Write Operation Log end ----->


def discountCode_Manager():
    print("[*]            旅遊金序號管理器")
    print("[*]         ↓請先選擇要執行的動作↓")
    print("[*]================模式選擇=================")
    print("[*]          1. 產生旅遊金序號")
    print("[*]          2. 銷毀旅遊金序號")
    print("[*]========================================")
    mode = input("[?]請選擇要執行的功能(輸入編號): ")

    while True:
        if mode in {"1", "2"}:
            break
        else:
            print("[!]請輸入正確的模式編號!")
    clearConsole()

    if mode == "1":
        discountCode()
        return

    print("[*]目前功能: 銷毀旅遊金序號")
    print("[*]========================================")
    codeToScrapped = input("[?]請輸入要銷毀之序號: ")
    scrapper = conn.cursor()
    scrapper.execute(searchCommand(listFrom="旅遊金序號", key="序號", searchBy=codeToScrapped))
    response = scrapper.fetchall()
    if len(response) != 1:
        print("[!]警告: 資料庫中有超過一組此序號")  # 理論上不會發生 這是以防萬一

    if response[0][2] == 1:
        print("[!]此序號已被兌換過了，建議保存已兌換過之序號，以便日後追蹤。")
        if input("[?]請問要繼續執行序號銷毀嗎?(y/n) ") in ("y", "Y"):
            pass
        else:
            return

    print("[*]使用狀態: ", end="")
    print("折扣碼尚未兌換" if response[0][2] == 0 else "折扣碼已兌換")
    print(f"[*]序號: {response[0][0]}\t金額: {response[0][1]}\t擁有者: {response[0][7]}\t使用期限: {response[0][6]}")

    if input("[?]請問確定要執行序號銷毀嗎(y/n): ") in ("n", "N"):
        return
    if input("[?]請再次確認要執行序號銷毀(y/n): ") in ("n", "N"):
        return

    # <----- 折扣碼銷毀 start ----->
    codeDelete = conn.cursor()
    codeDelete.execute(
        deleteCommand(
            listFrom="旅遊金序號",
            key = "序號",
            value = codeToScrapped
        )
    )
    print("[/]序號銷毀中...")
    conn.commit()
    print(f"[*]序號: {response[0][0]}已銷毀")
    codeDelete.close()
    # <----- 折扣碼銷毀 end ----->

    # <----- Write Operation Log start ----->
    operationTime = datetime.datetime.now()
    operationConfigBasePath = f"{os.getcwd()}\\操作紀錄"
    operationConfigPath = (
        operationConfigBasePath + "\\" + f"{operationTime.strftime('%Y-%m')}月份操作紀錄.ini"
    )
    if not os.path.isdir(operationConfigBasePath):
        os.mkdir(operationConfigBasePath)
    if not config.check_config_if_exist(operationConfigPath):
        config.make_config(operationConfigPath, configMode=3)

    operationLog = f"   銷毀時間: {operationTime}\n   >操作者: {db_settings['user']}\n   銷毀了折扣碼: {response[0][0]}\n"

    config.write_config(path=operationConfigPath, content=operationLog)
    # <----- Write Operation Log end ----->


def editClientProfile():
    editor = conn.cursor()
    print("[*]===============================================")
    clientID = input("[?]請輸入要更新資料的會員的身分證字號: ")
    editor.execute(searchCommand(listFrom="會員資料", key="身分證字號", searchBy=clientID))
    clientData = editor.fetchone()
    try:
        preData = f"姓名: {clientData[0]}    身分證字號: {clientData[1]}    生日: {clientData[2]}   電話: {clientData[3]}   餐食: {clientData[4]}   特殊需求: {clientData[5]}   社群暱稱: {clientData[6]}   身心障礙: {clientData[8]}"
    except TypeError:
        print(f"[!]資料庫中無 身分證字號: {clientID} 對應之資料")
        return
    print(
        "[*]======================================================客戶目前資料======================================================="
    )
    print("[>]" + preData)
    print(
        "[*]========================================================================================================================"
    )
    print("[*]如果只是要查詢會員資料請在確認完會員資料後輸入「e」即可")
    print(
        "[*]可編輯選項: 1.姓名    2.身分證字號    3.生日    4.電話    5.餐食    6.特殊需求    7.社群暱稱    8.身心障礙    delete: 刪除此筆會員資料    e: 不做任何操作"
    )
    editMode_Dict = {
        "1": "姓名",
        "2": "身分證字號",
        "3": "生日",
        "4": "電話",
        "5": "餐食",
        "6": "特殊需求",
        "7": "暱稱",
        "8": "身心障礙"
    }

    while True:
        editMode = input("[?]請選擇要編輯的項目: ")
        if editMode in ("e", "E"):
            print("[!]已取消編輯...")
            return 0
        elif editMode in ("1", "2", "3", "4", "5", "6", "7", "8", "delete"):
            break
        else:
            print('[!]請重新輸入「編輯選項」中的選項...')
            continue

    if editMode == "delete":
        while True:
            deleteCheck = input(f"[!]確定要刪除「{clientID}」的會員資料嗎(Y/N)? ")
            if deleteCheck in ("y", "Y"):
                editor.execute(
                    deleteCommand(listFrom="會員資料", key="身分證字號", value=clientID)
                )
                conn.commit()
                print(f"[*]已刪除 {clientID} 的會員資料")
                break
            elif deleteCheck in ("n", "N"):
                print(f"[!]已取消刪除 {clientID} 的會員資料")
                return 0
    else:
        newValue = input(f"[?]請問要將「{editMode_Dict[editMode]}」改為(請輸入欲更新之資料內容)? ")

        editor.execute(
            editCommand(
                listFrom="會員資料",
                key_toUpdate=editMode_Dict[editMode],
                value_toUpdate=newValue,
                searchBy_key="身分證字號",
                searchBy_value=clientID,
            )
        )
        conn.commit()

        if editMode == "2":
            clientID = newValue

        editor.execute(searchCommand(listFrom="會員資料", key="身分證字號", searchBy=clientID))
        clientDataNew = editor.fetchone()
        print(
            "[*]======================================================更新後的資料======================================================="
        )
        output = f"姓名: {clientDataNew[0]}    身分證字號: {clientDataNew[1]}    生日: {clientDataNew[2]}   電話: {clientDataNew[3]}   餐食: {clientDataNew[4]}   特殊需求: {clientDataNew[5]}   社群暱稱: {clientDataNew[6]}   身心障礙: {clientDataNew[8]}"
        print("[>]" + output)
        print(
            "[*]========================================================================================================================"
        )

    # <----- Write Operation Log start ----->
    operationConfigBasePath = f"{os.getcwd()}\\操作紀錄"
    operationTime = datetime.datetime.now()
    operationConfigPath = (
        operationConfigBasePath + "\\" + f"{operationTime.strftime('%Y-%m')}月份操作紀錄.ini"
    )

    if not os.path.isdir(operationConfigBasePath):
        os.mkdir(operationConfigBasePath)
    if not config.check_config_if_exist(operationConfigPath):
        config.make_config(operationConfigPath, configMode=3)

    if editMode != "delete":
        operationLog = f"   編輯時間: {operationTime}\n   >編輯前資料:\n   {preData}\n"

        config.write_config(path=operationConfigPath, content=operationLog)

        operationLog = f"   >編輯後資料:\n   {output}\n"
        config.write_config(path=operationConfigPath, content=operationLog)
    elif editMode == "delete":
        operationLog = f"   編輯時間: {operationTime}\n   >刪除了 {clientID} 的會員資料\n"

        config.write_config(path=operationConfigPath, content=operationLog)
    # <----- Write Operation Log end ----->


def addClientProfile():
    addClient = Client()
    print("[*]===============================================")
    addClient.name = input("[?]請輸入 客戶姓名: ")
    addClient.id = input("[?]請輸入 身分證字號: ")
    addClient.birthday = input("[?]請輸入 出生年月日: ")
    addClient.phone = input("[?]請輸入 連絡電話: ")
    addClient.foodType = input("[?]請輸入 餐食選項: ")
    addClient.specialNeeds = input("[?]請輸入 特殊需求: ")
    addClient.nickName = input("[?]請輸入 社群暱稱: ")
    addClient.travelDays = 0  # 新進客戶預設為0
    addClient.disability = input("[?]是否領有身心障礙手冊: ")

    editor = conn.cursor()
    editor.execute(
        insertCommand(
            listFrom="會員資料",
            key=("姓名", "身分證字號", "生日", "電話", "餐食", "特殊需求", "暱稱", "旅遊天數", "身心障礙"),
            value=(
                addClient.name,
                addClient.id,
                addClient.birthday,
                addClient.phone,
                addClient.foodType,
                addClient.specialNeeds,
                addClient.nickName,
                addClient.travelDays,
                addClient.disability
            ),
        )
    )
    conn.commit()
    editor.execute(searchCommand(listFrom="會員資料", key="身分證字號", searchBy=addClient.id))
    newData = editor.fetchall()[0]
    if len(editor.fetchall()) > 1:
        print("[!]警告: 此會員資料於資料庫中有重複，請回到主選單選擇「功能5」來處理資料庫重複之問題")
        return
        
    print(
        "[*]======================================================新增客戶資料======================================================="
    )
    printData = f"姓名: {newData[0]}    身分證字號: {newData[1]}    生日: {newData[2]}   電話: {newData[3]}   餐食: {newData[4]}   特殊需求: {newData[5]}   社群暱稱: {newData[6]}   旅遊天數: {newData[7]}    身心障礙: {newData[8]}"
    print("[>]" + printData)
    print(
        "[*]========================================================================================================================"
    )
    # <----- Write Operation Log start ----->
    operationConfigBasePath = f"{os.getcwd()}\\操作紀錄"
    operationTime = datetime.datetime.now()
    operationConfigPath = (
        operationConfigBasePath + "\\" + f"{operationTime.strftime('%Y-%m')}月份操作紀錄.ini"
    )

    if not os.path.isdir(operationConfigBasePath):
        os.mkdir(operationConfigBasePath)
    if not config.check_config_if_exist(operationConfigPath):
        config.make_config(operationConfigPath, configMode=3)

    operationLog = f"   新增時間: {operationTime}\n   >新增資料:\n   {printData}\n"

    config.write_config(path=operationConfigPath, content=operationLog)
    # <----- Write Operation Log end ----->


def dataRepeatCheck():
    print("[*]===============================================")
    repeateID_Dict = {}
    selectedList = []
    repeateChecker = conn.cursor()
    reader = conn.cursor()
    repeateChecker.execute("select * from `會員資料` group by `身分證字號` having count(*) > 1")
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
                searchCommand(listFrom="會員資料", key="身分證字號", searchBy=clientRepeat[1])
            )
            print(f"[*]以下為 {clientRepeat[1]} {clientRepeat[0]} 的每組重複之資料:")
            for idx, searchResult in enumerate(reader.fetchall()):
                repeateID_Dict[idx + 1] = Client()
                repeateID_Dict[idx + 1].name = searchResult[0]
                repeateID_Dict[idx + 1].id = searchResult[1]
                repeateID_Dict[idx + 1].birthday = searchResult[2]
                repeateID_Dict[idx + 1].phone = searchResult[3]
                repeateID_Dict[idx + 1].foodType = searchResult[4]
                repeateID_Dict[idx + 1].specialNeeds = searchResult[5]
                repeateID_Dict[idx + 1].nickName = searchResult[6]
                repeateID_Dict[idx + 1].travelDays = searchResult[7]
                repeateID_Dict[idx + 1].disability = searchResult[8]
                print(
                    f"[>]{idx+1}. 姓名: {repeateID_Dict[idx+1].name}\t身分證字號: {repeateID_Dict[idx+1].id}\t生日: {repeateID_Dict[idx+1].birthday}\t電話: {repeateID_Dict[idx+1].phone}\t餐食: {repeateID_Dict[idx+1].foodType}\t特殊需求: {repeateID_Dict[idx+1].specialNeeds}\t暱稱: {repeateID_Dict[idx+1].nickName}\t旅遊天數: {repeateID_Dict[idx+1].travelDays}\t身心障礙: {repeateID_Dict[idx+1].disability}"
                )
            while True:
                try:
                    selectFromRepeat = int(
                        input("[?]請從以上重複的資料當中，選擇一筆要保存的資料(輸入編號): ")
                    )  # reference: repeateID_Dict[ idx+1 ]
                    break
                except:
                    input("[!]輸入有誤，請輸入正確的保留版本編號")
            temp = repeateID_Dict[selectFromRepeat]
            selectedList.append(temp)
            print(
                f"[*]\t保存的版本:\n[*]\t{selectFromRepeat}. 姓名: {temp.name}\t身分證字號: {temp.id}\t生日: {temp.birthday}\t電話: {temp.phone}\t餐食: {temp.foodType}\t特殊需求: {temp.specialNeeds}\t暱稱: {temp.nickName}\t旅遊天數: {temp.travelDays}\t身心障礙: {temp.disability}"
            )
            print("[-]")
            input("[*]請按 Enter鍵 繼續選取...")
            print("[-]")
        clearConsole()
        print("[*]以下為最終選取的保留版本:")
        for selected in selectedList:
            print(
                f"[*]姓名: {selected.name}\t身分證字號: {selected.id}\t生日: {selected.birthday}\t電話: {selected.phone}\t餐食: {selected.foodType}\t特殊需求: {selected.specialNeeds}\t暱稱: {selected.nickName}\t旅遊天數: {selected.travelDays}\t身心障礙: {selected.disability}"
            )
        reChoose = input("[*]如果要重新選擇，請輸入「re」，如果確認要使用上述資料作為最新資料，直接按「Enter鍵」繼續")
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
                deleteCommand(listFrom="會員資料", key="身分證字號", value=client.id)
            )
            conn.commit()
            # re:ADD
            repeateChecker.execute(
                insertCommand(
                    listFrom="會員資料",
                    key=("姓名", "身分證字號", "生日", "電話", "餐食", "特殊需求", "暱稱", "旅遊天數", "身心障礙"),
                    value=(
                        client.name,
                        client.id,
                        client.birthday,
                        client.phone,
                        client.foodType,
                        client.specialNeeds,
                        client.nickName,
                        client.travelDays,
                        client.disability
                    ),
                )
            )
            conn.commit()
            print(f"[*]{client.name} 資料已更新 ")
        repeateChecker.execute("SELECT `身分證字號` FROM `會員資料` WHERE 1")
        print(f"[*]所有資料庫中重複的資料已更新完成 目前資料庫總共有: {len(repeateChecker.fetchall())} 筆資料")
    elif finalCheck_BeforeEdit in ("n", "N"):
        print("[*]已取消更新")
    # <----- Write Operation Log start ----->
    operationConfigBasePath = f"{os.getcwd()}\\操作紀錄"
    operationTime = datetime.datetime.now()
    operationConfigPath = (
        operationConfigBasePath + "\\" + f"{operationTime.strftime('%Y-%m')}月份操作紀錄.ini"
    )

    if not os.path.isdir(operationConfigBasePath):
        os.mkdir(operationConfigBasePath)
    if not config.check_config_if_exist(operationConfigPath):
        config.make_config(operationConfigPath, configMode=3)

    operationLog = f"   操作時間: {operationTime}\n   >更動名單:\n   {[client.name for client in selectedList]}\n"

    config.write_config(path=operationConfigPath, content=operationLog)
    # <----- Write Operation Log end ----->


def open_phpMyAdmin():
    print("[*]===============================================")
    phpMyAdmin_link = "http://" + db_settings["host"] + "/phpMyAdmin"
    webbrowser.open_new(phpMyAdmin_link)
    print("[*]已於預設瀏覽器中開啟: 網頁版管理介面(phpMyAdmin)")
    print("[*]===============================================")


def pinkbird_function(functionChoose, functionName):
    """
    功能清單
    type functionChoose: str
    """
    clearConsole()
    if functionName != "結束系統":
        print("[*]===============================================")
        print(f"[*]目前功能: {functionName}")
        print("[*]在各功能介面中，隨時可以按下「Ctrl + C」回到主選單介面")
    method = functionDefined.get(functionChoose, default)

    return method()


def exit_pinkbird_system():
    try:
        conn.close()
    except NameError:
        # 尚未成功連線就結束程式的狀況
        pass
    print(f"[!]程式結束...  本次執行時間: {datetime.datetime.now()-loginTime}")
    raise Endding


def overview():
    with conn.cursor() as cur:        
        cur.execute(countCommand("會員資料"))
        amount_of_clients = cur.fetchone()[0]
    
    while True:
        clearConsole()
        print(f"[*]========================================")
        print("[*]" + f"資料庫 {db_settings['database']} 總覽".center(37))
        print("[*]" + f"資料庫目前總人數為 {amount_of_clients} 人".center(32))
        print(f"[*]========================================")
        print("[*]目前支援分析的項目有:")
        print("[*]    1. 旅遊天數排名")
        print("[*]    2. 年齡層分布")
        print("[*]    3. 餐食種類分布")
        print("[*]    4. 身心障礙手冊總覽")
        print("[*]    5. 旅遊金序號總覽")
        print("[*]    e. 回到主選單")
        print("[*]" + "="*40)
        try:
            typeChoose = input("[?}請選擇要查詢之項目: ")
            if typeChoose in ("e", "E"):
                return
            typeChoose = int(typeChoose)
        except TypeError:
            print("[!]請勿輸入「數字」以外的數值!")
            input("[*]請按鍵盤上的「Enter」鍵以繼續...")
        except ValueError:
            print("[!]請勿輸入「選項」以外的數值!")
            input("[*]請按鍵盤上的「Enter」鍵以繼續...")

        if typeChoose not in range(1, 6):
            print("[!]請輸入正確的功能編號!")
            continue

        if typeChoose == 1:
            travelsDay_ranking_overview()
        elif typeChoose == 2:
            ages_overview()
        elif typeChoose == 3:
            foodType_overview()
        elif typeChoose == 4:
            disability_overview()
        elif typeChoose == 5:
            discountCode_overview()
        
        input("[*]請按鍵盤上的「Enter」鍵以繼續...")
    

def foodType_overview():
    with conn.cursor() as cur:
        cur.execute(countCommand("會員資料"))
        amount_of_clients = cur.fetchone()[0]
        cur.execute(countCommand("會員資料", "餐食", "葷食"))
        meatfood = cur.fetchone()[0]
        cur.execute(countCommand("會員資料", "餐食", "素食"))
        vegetarian = cur.fetchone()[0]
    
    print("[*]" + "="*40)
    print(f"[*]餐食為「素食」者共有 {vegetarian} 人")
    print(f"[*]餐食為「葷食」者共有 {meatfood} 人")
    print("[*]" + "="*40)
    print(f"[*]資料庫總人數為 {amount_of_clients} 人")


def ages_overview():
    age_0_3 = age_4_6 = age_7_12 = age_13_64 = age_65up = 0
    total_age = 0

    with conn.cursor() as cur:
        cur.execute(countCommand("會員資料"))
        amount_of_clients = cur.fetchone()[0]
        cur.execute(searchCommand_sp("會員資料", "生日"))
        births = cur.fetchall()
        for birth in births:
            age = year_cal.get_years_old(birth[0], datetime.date.today())
            total_age += age

            if age >= 0 and age <= 3:
                age_0_3 += 1
            elif age >= 4 and age <= 6:
                age_4_6 += 1
            elif age >= 7 and age <= 12:
                age_7_12 += 1
            elif age >= 13 and age <= 64:
                age_13_64 += 1
            elif age >= 65:
                age_65up += 1
        
    print("[*]" + "="*40)
    print(f"[*] 0  ~ 3   歲共有 {age_0_3} 人")
    print(f"[*] 4  ~ 6   歲共有 {age_4_6} 人")
    print(f"[*] 7  ~ 12  歲共有 {age_7_12} 人")
    print(f"[*] 13 ~ 64  歲共有 {age_13_64} 人")
    print(f"[*]   >= 65  歲共有 {age_65up} 人")
    print("[*]" + "="*40)
    print(f"[*]資料庫總人數為 {amount_of_clients} 人，平均 {total_age/amount_of_clients: 2.2f} 歲")


def disability_overview():
    command_base = "SELECT COUNT(*) FROM `會員資料` WHERE `身心障礙` LIKE "
    with conn.cursor() as cur:
        cur.execute(countCommand("會員資料"))
        amount_of_clients = cur.fetchone()[0]

        cur.execute(command_base + "'%是%'")
        disability_amount = cur.fetchone()[0]

        cur.execute(command_base + "'%輕度%'")
        disability_level_1 = cur.fetchone()[0]

        cur.execute(command_base + "'%中度%'")
        disability_level_2 = cur.fetchone()[0]

        cur.execute(command_base + "'%重度%'")
        disability_level_3 = cur.fetchone()[0]

    print("[*]" + "="*40)
    print(f"[*]資料庫: {db_settings['database']} 的 {amount_of_clients} 名會員中共有 {disability_amount} 人領有身心障礙手冊\n[*]分別為: ")
    print(f"[*]    輕度: {disability_level_1} 人")
    print(f"[*]    中度: {disability_level_2} 人")
    print(f"[*]    重度: {disability_level_3} 人")
    print("[*]" + "="*40)
    print(f"[*]資料庫總人數為 {amount_of_clients} 人")


def travelsDay_ranking_overview():
    with conn.cursor() as cur:
        cur.execute(countCommand("會員資料"))
        amount_of_clients = cur.fetchone()[0]

    while True:
        try:
            topNums = int(input(f"[?]請問要搜尋前幾名(輸入1~{amount_of_clients}之數值)? "))
            if topNums < 1 or topNums > amount_of_clients:
                raise IndexError
            break
        except ValueError:
            print("[!]請輸入數字，請勿輸入數字以外的格式!")
        except IndexError:
            print(f"[!]請確保你輸入的是『1 ~ {amount_of_clients}』之數值，數值不能超過資料數的人數!")

    with conn.cursor() as cur:
        command = "SELECT `姓名`, `旅遊天數` FROM `會員資料` ORDER BY `會員資料`.`旅遊天數` DESC LIMIT " + str(topNums)
        cur.execute(command)
        leaderboard = cur.fetchall()

    print("[*]" + "="*40)
    for idx, ranking in enumerate(leaderboard):
        print(f"[>]第{idx+1:3d} 名: {ranking[0]:4s} 共參加了 {ranking[1]:4d} 天旅遊行程")
    print("[*]" + "="*40)
    print(f"[*]資料庫總人數為 {amount_of_clients} 人")


def discountCode_overview():
    with conn.cursor() as cur:
        cur.execute(countCommand("旅遊金序號"))
        amount_of_discountCode = cur.fetchone()[0]
        cur.execute("SELECT SUM(`金額`) FROM `旅遊金序號` WHERE 1")
        total_value = cur.fetchone()[0]
        cur.execute("SELECT MAX(`金額`) FROM `旅遊金序號` WHERE 1")
        max_value = cur.fetchone()[0]
        cur.execute("SELECT MIN(`金額`) FROM `旅遊金序號` WHERE 1")
        min_value = cur.fetchone()[0]
        cur.execute("SELECT AVG(`金額`) FROM `旅遊金序號` WHERE 1")
        avg_value = cur.fetchone()[0]
        cur.execute("SELECT SUM(`金額`) FROM `旅遊金序號` WHERE `是否使用過` = '1'")
        used_value = cur.fetchone()[0]

    # 2021.09.02 fixed
    # TypeError: int() argument must be a string, a bytes-like object or a number, not 'NoneType'
    if used_value == None:
        used_value = 0

    print("[*]" + "="*40)
    print(f"[*]已發行之旅遊金序號總數為 {amount_of_discountCode} 張 -> 總價值: {total_value} 元")
    print("[*]" + "="*40)
    print(f"[*]已兌換的折扣金額為: {int(used_value): 6d} 元")
    print(f"[*]未兌換的折扣金額為: {int((total_value - used_value)): 6d} 元")
    print(f"[*]發行過最大的面額為: {max_value: 6d} 元")
    print(f"[*]發行過最小的面額為: {min_value: 6d} 元")
    print(f"[*]所有折扣碼面額平均: {avg_value: 6.2f} 元")
    print("[*]" + "="*40)


functionDefined = {
    "1": registeForm_processing,
    "2": discountCode_Manager,
    "3": editClientProfile,
    "4": addClientProfile,
    "5": dataRepeatCheck,
    "6": open_phpMyAdmin,
    "7": overview,
    "E": exit_pinkbird_system,
    "e": exit_pinkbird_system,
}

if __name__ == "__main__":
    # <----- System setting config start ----->
    if not config.check_config_if_exist(path=f"{os.getcwd()}\\config.ini"):
        print("[!]警告: 系統找不到 config.ini")
        print(f"[/]自動產生 config.ini 中...")

        configPath = f"{os.getcwd()}\\config.ini"
        config.make_config(configPath, configMode=1)

        print(f"[*]config.ini 產生成功 -> 檔案路徑: {configPath}")
        print("[!]訊息: 請在完成設定 config.ini 後再重新開啟程式")
        os.system("pause")
        sys.exit()
    configResult = config.load_config(path="./config.ini")
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
            "user": input("[?]帳號: "),
            "password": input("[?]密碼: "),
            "database": "pinkbird",
            "charset": "utf8",
        }
        print("[*]========================================")
        try:
            global conn
            print(
                f"[-]連接至資料庫 -> {db_settings['database']} 中, 路徑為: {db_settings['host']}:{db_settings['port']}"
            )
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
            retryLogin = input("[!]帳號或密碼有錯，請問是否要重新輸入，否則系統自動關閉(Y/N): ")
            loginSuccess = False
            if retryLogin in ("y", "Y"):
                retryLoginCount += 1
                continue
            else:
                exit_pinkbird_system()
        finally:
            # <----- Write Login Log start ----->
            configBasePath = f"{os.getcwd()}\\登入紀錄"
            configPath = (
                configBasePath + "\\" + f"{loginTime.strftime('%Y-%m')}月份-登入紀錄.ini"
            )
            if not os.path.isdir(configBasePath):
                os.mkdir(configBasePath)

            if not config.check_config_if_exist(configPath):
                config.make_config(configPath, configMode=2)

            if loginSuccess:
                loginLog = f"{loginTime}\t{db_settings['user']}\t{'登入成功'}\n"
            else:
                loginLog = f"{loginTime}\t{db_settings['user']}\t第 {retryLoginCount+1} 次嘗試登入失敗\n"

            config.write_config(path=configPath, content=loginLog)
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
        print("[*]" + "\t  2. 旅遊金序號管理")
        print("[*]" + "\t  3. 會員資料(可查詢、編輯或刪除)")
        print("[*]" + "\t  4. 手動新增會員資料")
        print("[*]" + "\t  5. 檢查會員資料是否重複")
        print("[*]" + "\t  6. 開啟網頁版管理介面")
        print("[*]" + "\t  7. 資料庫總覽")
        print("[*]" + "\t  e. 離開系統")
        print("[*]" + "=" * 40)
        print("[*]在各功能介面中，隨時可以按下「Ctrl + C」回到此主選單介面")
        functionChoose = input(f"[?]請選擇功能: ")

        if functionChoose not in functionDefined:
            print("[*]===============================================")
            input("[?]請重新輸入功能選單中之數字...")
            clearConsole()
            continue

        try:
            # <----- Write Operation Log start ----->
            operationTime = datetime.datetime.now()
            operationConfigBasePath = f"{os.getcwd()}\\操作紀錄"
            operationConfigPath = (
                operationConfigBasePath
                + "\\"
                + f"{operationTime.strftime('%Y-%m')}月份操作紀錄.ini"
            )
            if not os.path.isdir(operationConfigBasePath):
                os.mkdir(operationConfigBasePath)

            if not config.check_config_if_exist(operationConfigPath):
                config.make_config(operationConfigPath, configMode=3)

            if functionChoose == "1":
                operationName_inChinese = "產生出團名冊"
            elif functionChoose == "2":
                operationName_inChinese = "旅遊金序號管理"
            elif functionChoose == "3":
                operationName_inChinese = "會員資料(可查詢、編輯或刪除)"
            elif functionChoose == "4":
                operationName_inChinese = "手動新增會員資料"
            elif functionChoose == "5":
                operationName_inChinese = "檢查會員資料是否重複"
            elif functionChoose == "6":
                operationName_inChinese = "開啟網頁版管理介面"
            elif functionChoose == "7":
                operationName_inChinese = "資料庫總覽"
            elif functionChoose in ("e", "E"):
                operationName_inChinese = "結束系統"

            operationLog = (
                f"{operationTime}\t{db_settings['user']}\t{operationName_inChinese}\n"
            )

            config.write_config(path=operationConfigPath, content=operationLog)
            # <----- Write Operation Log end ----->

            pinkbird_function(functionChoose, functionName=operationName_inChinese)
        except Endding:
            pass
        except KeyboardInterrupt:
            print("\n[*]系統將回到主選單")
        finally:
            try:
                if operationName_inChinese != "結束系統":
                    input("[*]請按「Enter鍵」以繼續...")
                else:
                    input("[*]請按「Enter鍵」來結束程式...")
            except KeyboardInterrupt:
                pass
            # 結束每階段任務後清除 Console
            clearConsole()
    # <----- Main Loop end ----->
