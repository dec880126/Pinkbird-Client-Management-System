# -*- coding: utf-8 -*-
"""
PINKBIRD CLIENT MANAGEMENT SYSTEM
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
import sys
import os
import string
import secrets
import webbrowser
import threading
import time
from rich.progress import track

# ? Packages
import package.year_cal as year_cal
import package.config as config
from package.sql_command import *
from package.tools import set_cost, clearConsole, xlsx_DataFrame, default
from package.overview import *


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
        self.orgCost = "無"
        self.discountCode = "無"
        self.discountUsed = "無"
        self.discountValue = 0
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
    pass

class WrongDepartTypeChoose(Exception):
    pass

class Illegal_discountCode(Exception):
    pass


def registeForm_processing():
    # <---------- departMode selecting start ---------->
    print("[*]", '出團模式選擇'.center(50, '='))
    print("[*]模式選項: ")
    print("[*]  1. 報名表單「不」包含房型選項")
    print("[*]  2. 報名表單包含房型選項")
    print("[*]" + ''.center(50, '='))
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
    filePath = input("[?]請將檔案拉到程式畫面中...").replace('"', "").removesuffix(" ")
    try:
        if departMode == 1:
            try:
                # 2021.09.01 fixed
                # ValueError: Worksheet named '表單回應 1' not found
                df = pd.read_excel(
                    filePath,
                    sheet_name="表單回應 1",                    
                    # 無身心障礙手冊選項 -> B:F順序為: "身分證字號", "連絡電話", "上車地點", "序號", "座位"
                    # 有身心障礙手冊選項 -> B:G順序為: "身分證字號", "連絡電話", "上車地點", "身心障礙手冊", "序號", "座位"
                    usecols= "B:G" if disability_switch else "B:F"
                )
            except ValueError:
                df = pd.read_excel(
                    filePath,
                    sheet_name="Form Responses 1",
                    # 無身心障礙手冊選項 -> B:F順序為: "身分證字號", "連絡電話", "上車地點", "序號", "座位"
                    # 有身心障礙手冊選項 -> B:G順序為: "身分證字號", "連絡電話", "上車地點", "身心障礙手冊", "序號", "座位"
                    usecols= "B:G" if disability_switch else "B:F"
                )
        elif departMode == 2:
            try:
                df = pd.read_excel(
                    filePath,
                    sheet_name="表單回應 1",
                    # 無身心障礙手冊選項 -> B:H順序為: "身分證字號", "連絡電話", "上車地點", "房型", "同房者", "序號", "座位"
                    # 有身心障礙手冊選項 -> B:I順序為: "身分證字號", "連絡電話", "上車地點", "房型", "同房者", "身心障礙手冊", "序號", "座位"
                    usecols= "B:I" if disability_switch else "B:H"
                )
            except ValueError:
                df = pd.read_excel(
                    filePath,
                    sheet_name="Form Responses 1",
                    # 無身心障礙手冊選項 -> B:H順序為: "身分證字號", "連絡電話", "上車地點", "房型", "同房者", "序號", "座位"
                    # 有身心障礙手冊選項 -> B:I順序為: "身分證字號", "連絡電話", "上車地點", "房型", "同房者", "身心障礙手冊", "序號", "座位"
                    usecols= "B:I" if disability_switch else "B:H"
                )
        # print(df)
    except OSError:
        clearConsole()
        print("[*]" + ''.center(80, '='))
        print("[!]警告: 由於 Windows 系統不支援檔案名稱中有空格的程式操作 請將檔案名稱中的空格刪除後再重新執行")
        print("[*]" + ''.center(80, '='))
        print("[*]幫助: 範例: 粉鳥旅行社多日遊報名表單範例 (回覆).xlsx    <- 此為檔案名稱")
        print("[*]           通常空格存在於「(回覆)」的前面，刪除空格後程式即可正常執行!")
        print("[!]提醒: 空格的原因是因為 Google 端的設定，所以在匯入前要特別留意")
        print("[*]" + ''.center(80, '='))
        input("[*]請按任意鍵回到 粉鳥旅行社會員資料庫管理系統-功能選擇介面...")
        return
    # <---------- reading xlsx end ---------->

    # <---------- depart info start ---------->
    while True:
        groupName = input('[?]請輸入團名： ')
        departDay_raw = input("[?]請輸入出團日期(YYYY.MM.DD)： ")
        departDay_raw = departDay_raw.split(".")
        try:
            departDay = datetime.date(
                year=int(departDay_raw[0]),
                month=int(departDay_raw[1]),
                day=int(departDay_raw[2]),
            )
            if datetime.date.today() > departDay:
                print("[!]提醒: 出團日期是過去的日期！") # 2021.09.01 update
                if input('[?]是否要繼續進行(y/n)? ') in ('Y', 'y'):
                    pass
                else:
                    print('[!]請重新輸入出團日期...')
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
            IDhere = str(df.at[idx, df.columns[0]]).replace(' ', '')

            # 排除excel檔中的空格狀況
            if isinstance(IDhere, float):
                continue

            attendClient_Dict[IDhere] = Client()

            # 順序為: 
            #   無身心障礙手冊 -> 0."身分證字號", 1."連絡電話", 2."上車地點", 3."序號", 4."座位"
            #   有身心障礙手冊 -> 0."身分證字號", 1."連絡電話", 2."上車地點", 3."身心障礙手冊", 4."序號", 5."座位"
            attendClient_Dict[IDhere].id = IDhere
            attendClient_Dict[IDhere].phone = df.at[idx, df.columns[1]]
            attendClient_Dict[IDhere].location = df.at[idx, df.columns[2]]
            if disability_switch:
                attendClient_Dict[IDhere].disability = str(df.at[idx, df.columns[3]])
            attendClient_Dict[IDhere].discountCode = str(df.at[idx, df.columns[4]]) if disability_switch else str(df.at[idx, df.columns[3]])
            attendClient_Dict[IDhere].seat = str(df.at[idx, df.columns[5]]) if disability_switch else str(df.at[idx, df.columns[4]])
            attendClient_Dict[IDhere].roomType = None
            attendClient_Dict[IDhere].roommate = None
            

            # 測試讀取錯誤的狀況 如果出正常則continue，否則系統將顯示提醒訊息
            # print(attendClient_Dict[IDhere].disability)
            # if "是" in attendClient_Dict[IDhere].disability or "否" in attendClient_Dict[IDhere].disability:
            # 2021.09.07關閉身心障礙手冊功能
            continue

            print("[!]可能是出團表單中包含房型選項，請重新選擇出團模式")
            raise KeyboardInterrupt
    elif departMode == 2:
        for idx in range(df.shape[0]):
            IDhere = str(df.at[idx, df.columns[0]]).replace(' ', '')
            # 排除excel檔中的空格狀況
            if isinstance(IDhere, float):
                continue
            attendClient_Dict[IDhere] = Client()

            # 順序為:
            #   無身心障礙手冊 -> 0."身分證字號", 1."連絡電話", 2."上車地點", 3."房型", 4."同房者", 5."序號", 6."座位"
            #   有身心障礙手冊 -> 0."身分證字號", 1."連絡電話", 2."上車地點", 3."房型", 4."同房者", 5."身心障礙手冊", 6."序號", 7."座位"
            attendClient_Dict[IDhere].id = IDhere
            attendClient_Dict[IDhere].phone = df.at[idx, df.columns[1]]
            attendClient_Dict[IDhere].location = df.at[idx, df.columns[2]]
            attendClient_Dict[IDhere].roomType = df.at[idx, df.columns[3]]
            attendClient_Dict[IDhere].roommate = df.at[idx, df.columns[4]]
            if disability_switch:
                attendClient_Dict[IDhere].disability = df.at[idx, df.columns[5]]
            attendClient_Dict[IDhere].discountCode = str(df.at[idx, df.columns[6]]) if disability_switch else str(df.at[idx, df.columns[5]])
            attendClient_Dict[IDhere].seat = df.at[idx, df.columns[7]] if disability_switch else str(df.at[idx, df.columns[6]])
    # <---------- client class processing end ---------->
    try:
        print('[!]Excel檔中有空行 -> 已自動排除 !')
        del attendClient_Dict['nan']
    except KeyError:
        pass

    try:
        while True:
            cursor = conn.cursor()
            print(f"[-]正在向資料庫 {db_settings['database']} 請求資料")

            # 2021.09.04 fixed: 修正遇到未註冊會員時的判斷與處理機制
            clientIDs = [client.id for client in attendClient_Dict.values()]
            clientDatas = {}
            illegal_IDs = []

            for step, ID in zip(track(clientIDs, description="[\]正在確認會員資料中"), clientIDs):
                cursor.execute(
                    searchCommand(
                        listFrom="會員資料",
                        key="身分證字號",
                        searchBy=ID,
                    )
                )
                
                clientDatas[ID] = cursor.fetchone()

                if clientDatas[ID] == None:                
                    illegal_IDs.append(ID)
                time.sleep(0.005)
            print("[*]確認完成 ! ")

            # 確認無不存在之會員資料才繼續作業，否則進行會員資料補註冊
            if not illegal_IDs:
                break

            if illegal_IDs:
                print("[*]" + ''.center(80, '='))
                print("[!]下列身份證字號並未在資料庫中 ! 可能是輸入錯誤或是尚未註冊")
                for idx, ID in enumerate(illegal_IDs):
                    print(f"[>]\t{idx+1}. 身份證字號: {ID} ")
                print("[*]" + ''.center(80, '='))
                while True:
                    Is_Continue_Add_Client = input("[?]是否要直接新增會員資料？(y/n)? ")
                    if Is_Continue_Add_Client in ('Y', 'y'):
                        for idx, ID in enumerate(illegal_IDs):
                            print(f"[>]\t{idx+1}. 身份證字號: {ID} ")
                            addClientProfile(clientID=ID, disability_switch=True)
                        break
                    elif Is_Continue_Add_Client in ('N', 'n'):
                        print("[*]請在確認完出團清單中的會員編號皆完成註冊後，再重新執行出團作業 ! ")
                        return

                
        clearConsole()
        print("[*]" + ''.center(80, '='))
        print("[*]以下為查詢結果:")

        for step, ID in zip(track(clientIDs, description="[\]處理中"), clientIDs):
            # <---------- client Processing start ---------->
            item = clientDatas[ID]           

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
            client.orgCost = cost
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
                        codeDeadline_List = codeDeadline[0].split(".")  # codeDeadline = [YYYY, MM, DD]
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
                            client.orgCost = cost
                            client.discountValue = code_discount
                            
                            # 序號在有效期限內才執行兌換程序
                            for k, v in zip(
                                ['是否使用過', '使用者', '使用日期'], [1, item[0], str(departDay)]
                            ):
                                sql_operator(
                                    connect=conn,
                                    instruction=editCommand(
                                        listFrom='旅遊金序號',
                                        key_toUpdate=k,
                                        value_toUpdate=v,
                                        searchBy_key='序號',
                                        searchBy_value=client.discountCode
                                    ),
                                    is_fetchAll=False,
                                    is_commit=True
                                )
                            print(f"[!]{item[0]} 兌換了 {code_discount} 元的優惠券!     詳細資訊: {client.orgCost}元 -> {client.orgCost - client.discountValue}元")
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

            client.discountUsed = code_discount if code_valid else 0

            if warningFlag:
                client.alertMsg = ""
                if codeHasBeenUsed:
                    client.alertMsg += "序號已被使用過 "
                if codeExpired:
                    client.alertMsg += f'序號已於 {codeDeadline} 過期 '
                if not code_exist:
                    client.alertMsg += f'序號: {client.discountCode} 不存在 '

        # <----- Write Operation Log start ----->
        operationLog = operationLog = f"出團日期: {departDay.strftime('%Y.%M.%D')} -> 出團名單: {tuple([client.name for client in attendClient_Dict.values()])}"
        writeOperationLog(
            connect=conn_log,
            user=db_settings["user"],
            content=operationLog
        )
        # <----- Write Operation Log end ----->

        # <----- Write Travel Log start ----->
        writeTravelLog(
            connect=conn_log,
            date='.'.join(departDay_raw),
            groupName=groupName,
            days=travelDays,
            costs=costList,
            attends=[client.name for client in attendClient_Dict.values()]
        )
        # <----- Write Travel Log end ----->

        # <---------- Making xlsx start ---------->
        if departMode == 1:
            df = xlsx_DataFrame(
                clientList=attendClient_Dict.values(),
                mode="excluding_roomType"
            )
        elif departMode == 2:
            df = xlsx_DataFrame(
                clientList=attendClient_Dict.values(),
                mode="including_roomType"
            )
        print("[*]" + ''.center(50, '='))
        print(df)
        print("[*]" + ''.center(50, '='))

        excelName = "出團清冊" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".xlsx"
        df.to_excel(excelName, sheet_name="出團清冊", index=False, na_rep="空值")
        print("[*]已自動產生 -> " + excelName)
        # <---------- Making xlsx end ---------->
    except WrongDepartTypeChoose:
        print("[*]" + ''.center(50, '='))
        print("[!]警告: 可能在出團模式選擇處選擇錯誤，請確認輸入的Excel表格是否為有包含房型選項的格式，確認後請重新選擇出團模式為「報名表單包含房型選項」")
        print("[*]" + ''.center(50, '='))
    finally: 
        pass


def generate_discountCode(codeAmount, randomAmount, codeValue, prefix, clientName, deadline):
    code = conn.cursor()
    codeClass = {}

    for _ in range(codeAmount):
        while True:
            # <----- 亂碼產生 start ----->
            # 由序號擁有人之身分證字號數字9碼 + 五位亂數 + 序號面額
            codeKey = prefix + "".join(
                secrets.choice(string.ascii_letters) for _ in range(randomAmount)
            ) + str(codeValue)
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
    print("[*]由序號擁有人之身分證字號數字9碼 + 五位亂數 + 序號面額 -> 組合而成")
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
    operationLog = f"共產生了 {discountNums} 張 屬於 {clientName} 的 {discountValue} 元的折扣碼"
    writeOperationLog(
        connect=conn_log,
        user=db_settings["user"],
        content=operationLog
    )
    # <----- Write Operation Log end ----->


def discountCode_Manager():
    print("[*]            旅遊金序號管理器")
    print("[*]         ↓請先選擇要執行的動作↓")
    print("[*]================模式選擇=================")
    print("[*]          1. 產生旅遊金序號")
    print("[*]          2. 銷毀旅遊金序號")
    print("[*]========================================")   

    while True:
        mode = input("[?]請選擇要執行的功能(輸入編號): ")
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

    # 2021.09.08 fixed
    if len(response) == 0:
        print(f"[!]警告: 序號({codeToScrapped})不存在，請確認輸入的序號是正確的 !")
        print("[*]請確認序號的格式為: 身分證字號9碼數字 + 序號金鑰 + 序號面額")
        print("[*]備註: 若為旅行社發行序號為Pinkbird開頭")
        return

    if len(response) != 1:
        # 理論上不會發生
        print("[!]警告: 資料庫中有超過一組此序號")

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
    operationLog = f"銷毀了折扣碼: {response[0][0]}"
    writeOperationLog(
        connect=conn_log,
        user=db_settings["user"],
        content=operationLog
    )
    # <----- Write Operation Log end ----->


def editClientProfile():
    editor = conn.cursor()
    print("[*]" + '會員資料查詢(編輯)器'.center(50, '='))
    for idx, col in column_Dict.items():
        print('[*]' + f'\t{idx}. {col}')
    while True:
        searchType = input('[?]要使用何種資料來索引?')
        try:
            if searchType in column_Dict.keys():
                break
        except IndexError:
            print('[!]請輸入數字編號！')

        print('[!]' + '請輸入正確的索引編號...')
    searchKey = column_Dict[searchType]
    searchValue = input(f"[?]請輸入要更新資料的會員的 {searchKey}: ")
    editor.execute(searchCommand(listFrom="會員資料", key=searchKey, searchBy=searchValue))
    clientData = editor.fetchall()
    if len(clientData) == 0:
        print(f"[!]資料庫中無 {searchKey}: {searchValue} 對應之資料")
        return
    elif len(clientData) > 1:
        print('[!]' + f'資料庫中有 {len(clientData)} 筆 {searchKey} 為 {searchValue} 的資料')
    
    for idx in range(len(clientData)):
        print('[*]' + f' {idx + 1}. {searchKey}: {searchValue} 的會員資料'.center(80, '='))
        print('[*]', end='')
        for key, value in column_Dict.items():
            print(f'{value}: {clientData[idx][int(key) - 1]}', end='\t')

        print('\n')
    print('[*]' + ''.center(80, '='))
    print("[*]如果只是要查詢會員資料請在確認完會員資料後直接按下 Enter 即可")
    print("[*]可編輯選項: ")
    for idx, key in enumerate(column_Dict.values()):
        print('[*]' + f'\t{idx + 1}. {key}')
    else:
        print('[*]' + 'delete: 刪除此筆會員資料')
    print('[*]' + ''.center(80, '='))
    while True:
        if len(clientData) > 1:
            try:
                print('[!]' + '按下「Ctrl + C」可取消作業回到主畫面')
                select_data_to_edit = int(input("[?]請選擇要編輯的資料對象: "))
                if select_data_to_edit in range(1, len(clientData)+1):
                    select_data_to_edit = select_data_to_edit - 1
                else:
                    print('[!]' + f'請輸入正確的索引編號(1~{len(clientData)})...')
                    continue
            except ValueError:
                print('[!]' + f'請輸入正確的索引編號(1~{len(clientData)})...')
                continue
        else:
            select_data_to_edit = 0
        print('[*]', end='')
        for key, value in column_Dict.items():
            print(f'{value}: {clientData[select_data_to_edit][int(key) - 1]}', end='\t')
        editMode = input("\n[?]請選擇要編輯的項目: ")

        ID_of_edit_target = clientData[select_data_to_edit][1]

        if editMode == "":
            print("[!]已取消編輯...")
            return
        elif editMode in column_Dict.keys() or editMode == 'delete':
            break
        else:
            print('[!]請重新輸入「編輯選項」中的選項...')
            continue

    if editMode == "delete":
        while True:
            deleteCheck = input(f"[!]確定要刪除「{searchValue}」的會員資料嗎(Y/N)? ")
            if deleteCheck in ("y", "Y"):
                editor.execute(
                    deleteCommand(listFrom="會員資料", key='身分證字號', value=ID_of_edit_target)
                )
                conn.commit()
                print(f"[*]已刪除 {searchValue} 的會員資料")
                break
            elif deleteCheck in ("n", "N"):
                print(f"[!]已取消刪除 {searchValue} 的會員資料")
                return 0
    else:
        while True:
            newValue = input(f"[?]請問要將「{column_Dict[editMode]}」改為(請輸入欲更新之資料內容)? ")
            if newValue == '':
                is_continue = input('[!]尚未輸入內容，要繼續編輯請輸入「Y」，否則按「Enter」來取消編輯。') in ('Y', 'y')
                if is_continue:
                    continue
                elif is_continue == '':
                    print('[!]已取消編輯！')
                    return

            if column_Dict[editMode] == '生日':
                bithday = newValue.split(".")

                try:
                    datetime.date(
                        year=int(bithday[0]),
                        month=int(bithday[1]),
                        day=int(bithday[2]),
                    ).strftime("%Y.%m.%d")
                except IndexError:
                    print("[!]日期輸入格式錯誤，格式為（YYYY.MM.DD），例如：2021.01.01。")
                    continue
                except ValueError:
                    print("[!]日期輸入格式錯誤，格式為（YYYY.MM.DD），例如：2021.01.01。")
                    continue
            break

        editor.execute(
            editCommand(
                listFrom="會員資料",
                key_toUpdate=column_Dict[editMode],
                value_toUpdate=newValue,
                searchBy_key='身分證字號',
                searchBy_value=ID_of_edit_target,
            )
        )
        conn.commit()

        if editMode == "2":
            searchValue = newValue

        editor.execute(searchCommand(listFrom="會員資料", key='身分證字號', searchBy=ID_of_edit_target))
        clientDataNew = editor.fetchone()
        print(
            "[*]======================================================更新後的資料======================================================="
        )
        if disability_switch:
            output = f"姓名: {clientDataNew[0]}    身分證字號: {clientDataNew[1]}    生日: {clientDataNew[2]}   電話: {clientDataNew[3]}   餐食: {clientDataNew[4]}   特殊需求: {clientDataNew[5]}   社群暱稱: {clientDataNew[6]}   身心障礙: {clientDataNew[8]}"
        else:
            output = f"姓名: {clientDataNew[0]}    身分證字號: {clientDataNew[1]}    生日: {clientDataNew[2]}   電話: {clientDataNew[3]}   餐食: {clientDataNew[4]}   特殊需求: {clientDataNew[5]}   社群暱稱: {clientDataNew[6]}"
        print("[>]" + output)
        print(
            "[*]========================================================================================================================"
        )

    # <----- Write Operation Log start ----->
    if editMode != "delete":
        preData = ''
        for idx, value in enumerate(column_Dict.values()):
            preData += f'{value}: {clientDataNew[idx]}\t'

        operationLog = f"編輯前資料: {preData}"
        writeOperationLog(
            connect=conn_log,
            user=db_settings["user"],
            content=operationLog
        )

        operationLog = f"編輯後資料: {output}"
        writeOperationLog(
            connect=conn_log,
            user=db_settings["user"],
            content=operationLog
        )
    elif editMode == "delete":
        operationLog = f"刪除了 {searchValue} 的會員資料"

        writeOperationLog(
            connect=conn_log,
            user=db_settings["user"],
            content=operationLog
        )
    # <----- Write Operation Log end ----->


def addClientProfile(clientID = None, disability_switch = True):
    editor = conn.cursor()

    while True:
        try:
            addClient = Client()
            if clientID is None:
                print("[*]" + "".center(50, "="))
                addClient.id = input("[?]請輸入 身分證字號: ")
            else:
                print("[*]" + f"身分證字號： {clientID}".center(50, "="))
                addClient.id = clientID

            editor.execute(
                searchCommand(
                    listFrom='會員資料',
                    key='身分證字號',
                    searchBy=addClient.id
                )
            )
            _data = editor.fetchall()
            _data_amount = len(_data)
            try:
                if _data[0] != None:
                    for _ in range(5):
                        print('[*]')
                    print(f'[!]身分證字號: {addClient.id} 資料已在會員資料庫中 !  (共 {_data_amount} 筆)')
                    print(f'[>]\t會員資料: {_data[0]}')
                    for _ in range(5):
                        print('[*]')
                    return
            except IndexError:
                pass

            addClient.name = input("[?]請輸入 客戶姓名: ")
            addClient.birthday = input("[?]請輸入 出生年月日(民國曆/西元曆皆可): ")
            addClient.phone = input("[?]請輸入 連絡電話: ")
            addClient.foodType = input("[?]請輸入 餐食選項: ")
            addClient.specialNeeds = input("[?]請輸入 特殊需求: ")
            addClient.nickName = input("[?]請輸入 社群暱稱: ")
            addClient.travelDays = 0  # 新進客戶預設為0
            if disability_switch:
                addClient.disability = input("[?]是否領有身心障礙手冊: ")
            
            input("[?]請確認以上資料正確無誤後，按下 Enter 繼續，如有錯誤，請按「Ctrl + C」來重新輸入。")

            if disability_switch:
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
            else:
                editor.execute(
                    insertCommand(
                        listFrom="會員資料",
                        key=("姓名", "身分證字號", "生日", "電話", "餐食", "特殊需求", "暱稱", "旅遊天數"),
                        value=(
                            addClient.name,
                            addClient.id,
                            addClient.birthday,
                            addClient.phone,
                            addClient.foodType,
                            addClient.specialNeeds,
                            addClient.nickName,
                            addClient.travelDays
                        ),
                    )
                )
            break
        except KeyboardInterrupt:
            return
    conn.commit()
    editor.execute(searchCommand(listFrom="會員資料", key="身分證字號", searchBy=addClient.id))
    newData = editor.fetchall()[0]
    if len(editor.fetchall()) > 1:
        print("[!]警告: 此會員資料於資料庫中有重複，請回到主選單選擇「功能5」來處理資料庫重複之問題")
        return
        
    print(
        "[*]======================================================新增客戶資料======================================================="
    )
    if disability_switch:
        printData = f"姓名: {newData[0]}    身分證字號: {newData[1]}    生日: {newData[2]}   電話: {newData[3]}   餐食: {newData[4]}   特殊需求: {newData[5]}   社群暱稱: {newData[6]}   旅遊天數: {newData[7]}    身心障礙: {newData[8]}"
    else:
        printData = f"姓名: {newData[0]}    身分證字號: {newData[1]}    生日: {newData[2]}   電話: {newData[3]}   餐食: {newData[4]}   特殊需求: {newData[5]}   社群暱稱: {newData[6]}   旅遊天數: {newData[7]}"
    print("[>]" + printData)
    print(
        "[*]========================================================================================================================"
    )
    # <----- Write Operation Log start ----->
    operationLog = f"新增資料: {printData}"
    writeOperationLog(
        connect=conn_log,
        user=db_settings["user"],
        content=operationLog
    )
    # <----- Write Operation Log end ----->


def dataRepeatCheck():
    print("[>]" + '正在執行重複會員資料檢查......')
    repeateID_Dict = {}
    selectedList = []
    response = sql_operator(
        connect=conn,
        instruction="select * from `會員資料` group by `身分證字號` having count(*) > 1",
        is_fetchAll=True,
        is_commit=False
    )
    
    if len(response) == 0:
        print("[*]會員資料庫目前無重複資料!")
        return
    else:
        input('[!]會員資料庫中有重複的會員資料，請按下「Enter」來處理重複資料。')
    
    columeNames = sql_operator(
        connect=conn,
        instruction=getColumeNames(tableName='會員資料'),
        is_fetchAll=True,
        is_commit=False
    )
    columeNames = tuple([colName[0] for colName in columeNames])
    
    while True:
        print("[*]" + '以下為重複會員資料之名單'.center(50, '='))
        for clientRepeat in response:
            print(f"[>]姓名: {clientRepeat[0]} 身分證字號: {clientRepeat[1]}")
        input("[*]請按 Enter鍵 開始選擇保留版本")
        clearConsole()

        # <----- choosing start ----->
        for clientRepeat in response:
            print(f"[>]姓名: {clientRepeat[0]} 身分證字號: {clientRepeat[1]}")
            clientData = sql_operator(
                connect=conn,
                instruction=searchCommand(listFrom="會員資料", key="身分證字號", searchBy=clientRepeat[1]),
                is_fetchAll=True,
                is_commit=False
            )
            print(f"[*]以下為 {clientRepeat[1]} {clientRepeat[0]} 的每組重複之資料:")
            for idx, searchResult in enumerate(clientData):
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
                    f"[>]{idx+1}. 姓名: {repeateID_Dict[idx+1].name}\t" + 
                    f"身分證字號: {repeateID_Dict[idx+1].id}\t" + 
                    f"生日: {repeateID_Dict[idx+1].birthday}\t" + 
                    f"電話: {repeateID_Dict[idx+1].phone}\t" + 
                    f"餐食: {repeateID_Dict[idx+1].foodType}\t" + 
                    f"特殊需求: {repeateID_Dict[idx+1].specialNeeds}\t" + 
                    f"暱稱: {repeateID_Dict[idx+1].nickName}\t" + 
                    f"旅遊天數: {repeateID_Dict[idx+1].travelDays}\t" + 
                    f"身心障礙: {repeateID_Dict[idx+1].disability}"
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
        for clientRepeat, selected in zip(response, selectedList):
            print('='*50)
            if clientRepeat[0] != selected.name:
                print(f'[>]姓名: {clientRepeat[0]} 更改為 -> {selected.name}')
            else:
                print(f'[>]姓名: {clientRepeat[0]} -> 無更改')

            if clientRepeat[1] != selected.id:
                print(f'[>]身分證字號: {clientRepeat[1]} 更改為 -> {selected.id}')
            else:
                print(f'[>]身分證字號: {clientRepeat[1]} -> 無更改')

            if clientRepeat[2] != selected.birthday:
                print(f'[>]生日: {clientRepeat[2]} 更改為 -> {selected.birthday}')
            else:
                print(f'[>]生日: {clientRepeat[2]} -> 無更改') 
            
            if clientRepeat[3] != selected.phone:
                print(f'[>]電話: {clientRepeat[3]} 更改為 -> {selected.phone}')
            else:
                print(f'[>]電話: {clientRepeat[3]} -> 無更改') 
            
            if clientRepeat[4] != selected.foodType:
                print(f'[>]餐食: {clientRepeat[4]} 更改為 -> {selected.foodType}')
            else:
                print(f'[>]電話: {clientRepeat[4]} -> 無更改') 

            if clientRepeat[5] != selected.specialNeeds:
                print(f'[>]特殊需求: {clientRepeat[5]} 更改為 -> {selected.specialNeeds}')
            else:
                print(f'[>]特殊需求: {clientRepeat[5]} -> 無更改') 

            if clientRepeat[6] != selected.nickName:
                print(f'[>]暱稱: {clientRepeat[6]} 更改為 -> {selected.nickName}')
            else:
                print(f'[>]暱稱: {clientRepeat[6]} -> 無更改') 

            if clientRepeat[7] != selected.travelDays:
                print(f'[>]旅遊天數: {clientRepeat[7]} 更改為 -> {selected.travelDays}')
            else:
                print(f'[>]旅遊天數: {clientRepeat[7]} -> 無更改') 

            if clientRepeat[8] != selected.disability:
                print(f'[>]身心障礙: {clientRepeat[8]} 更改為 -> {selected.disability}')
            else:
                print(f'[>]身心障礙: {clientRepeat[8]} -> 無更改') 

        reChoose = input("[*]如果要重新選擇，請輸入「re」，如果確認要使用上述資料作為最新資料，直接按「Enter鍵」繼續")
        if reChoose != "re":
            break
        selectedList = []
        clearConsole()
        # <----- choosing end ----->

    finalCheck_BeforeEdit = input("[?]是否確定要更新資料(y/n): ")
    update_success = []
    if finalCheck_BeforeEdit in ('y, "Y'):
        for client in selectedList:
            try:
                # DELETE
                sql_operator(
                    connect=conn,
                    instruction=deleteCommand(listFrom="會員資料", key="身分證字號", value=client.id),
                    is_fetchAll=False,
                    is_commit=False
                )
                # re:ADD
                sql_operator(
                    connect=conn,
                    instruction=insertCommand(
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
                        )
                    ),
                    is_fetchAll=False,
                    is_commit=False
                )
                update_success.append(client.name)
            except Exception as errorMsg:
                print(f'[!]在處理會員：{client.name}({client.id})的資料時發生問題！')
                print(f'[!]錯誤資訊： {errorMsg}')
        else:
            # 確認都正常運作後再commit
            conn.commit()
        print(f"[*]{update_success} 的資料已更新 ")
        result = sql_operator(
            connect=conn,
            instruction="SELECT `身分證字號` FROM `會員資料` WHERE 1",
            is_fetchAll=True,
            is_commit=False
        )
        print(f"[*]所有資料庫中重複的資料已更新完成 目前資料庫總共有: {len(result)} 筆資料")
    elif finalCheck_BeforeEdit in ("n", "N"):
        print("[*]已取消更新")

    # <----- Write Operation Log start ----->
    operationLog = f"更動名單: {[client.name for client in selectedList]}"
    writeOperationLog(
        connect=conn_log,
        user=db_settings["user"],
        content=operationLog
    )
    # <----- Write Operation Log end ----->


def open_phpMyAdmin():
    print("[*]===============================================")
    phpMyAdmin_link = "http://" + db_settings["host"] + "/phpMyAdmin"
    webbrowser.open_new(phpMyAdmin_link)
    print("[*]已於預設瀏覽器中開啟: 網頁版管理介面(phpMyAdmin)")
    print("[*]===============================================")


def open_github():
    print("[*]===============================================")
    github_link = "https://github.com/dec880126/Pinkbird-Client-Management-System"
    webbrowser.open_new(github_link)
    print("[*]已於預設瀏覽器中開啟: Pinkbird-Client-Management-System(GitHub)")
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
    totalTime = str(datetime.datetime.now()-loginTime).split(':')
    totalTime = f'{totalTime[0]}:{totalTime[1]}:{totalTime[2].split(".")[0]}'
    print(f"[!]程式結束...  本次執行時間: {totalTime}")
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
            travelsDay_ranking_overview(connection=conn)
        elif typeChoose == 2:
            ages_overview(connection=conn)
        elif typeChoose == 3:
            foodType_overview(connection=conn)
        elif typeChoose == 4:
            disability_overview(
                connection=conn,
                database=db_settings["database"]
            )
        elif typeChoose == 5:
            discountCode_overview(connection=conn)

        input('[*]請按「Enter」以繼續。')


def change_disability_functions():
    # 2021.09.08 update
    print("[*]===============================================")
    global disability_switch
    t = disability_switch
    disability_switch = not disability_switch
    print(f"[*]已將身心障礙開關由 {t} 改為 {disability_switch}")


def list_all_ClientData():
    db_Name = '會員資料'
    result = sql_operator(
        connect=conn,
        instruction=f'SELECT * FROM `{db_Name}`',
        is_fetchAll=True
    )

    for idx, data in enumerate(result):
        printData = ''
        for colName, col in zip(column_Dict.values(), data):
            printData += f'{colName}: {col}\t'
        print(f'[*] {int(idx) + 1}. {printData}')


functionDefined = {
    # 一般指令
    "1": registeForm_processing,
    "2": discountCode_Manager,
    "3": editClientProfile,
    "4": addClientProfile,
    # "5": dataRepeatCheck,
    "5": open_phpMyAdmin,
    "6": overview,
    "7": list_all_ClientData,
    # "i": open_github,
    "e": exit_pinkbird_system,
    # 進階指令
    "changeDisabilityFunctions": change_disability_functions
}

def connect_sql_server():
    global loginSuccess

    # 使用者帳號有可能會錯誤 故需要一個確保能正常運作的帳號來紀錄Log
    db_log_settings = {
        "host": db_settings["host"],
        "port": db_settings["port"],
        "user": configResult["log-user"],
        "password": configResult["log-password"],
        "database": configResult["log-database"],
        "charset": "utf8",
    }
    
    try:
        global is_IP_allow
        global conn, conn_log
        conn_log = pymysql.connect(**db_log_settings)
        conn = pymysql.connect(**db_settings)
        loginSuccess = True
    except pymysql.err.OperationalError:
        loginSuccess = False
        is_IP_allow = True
    except pymysql.err.InternalError:
        is_IP_allow = False

if __name__ == "__main__":
    # Optional Switch
        # 2019.09.07 updates: 身心障礙手冊功能開關(Boolean)，決定後續所有功能是否開啟身心障礙手冊相關功能
    global disability_switch
    disability_switch = False

    # <----- System setting config start ----->
    if not config.check_config_if_exist(path=f"{os.getcwd()}\\config.ini"):
        print("[!]警告: 系統找不到 config.ini")
        print(f"[/]正在自動產生 config.ini ...")

        configPath = f"{os.getcwd()}\\config.ini"
        config.make_config(configPath, configMode=1)

        print(f"[*]config.ini 產生成功 -> 檔案路徑: {configPath}")
        print("[!]訊息: 請在完成 config.ini 配置後再重新開啟程式")
        os.system("pause")
        sys.exit()
    configResult = config.load_config(path="./config.ini")
    # <----- System setting config end ----->
    loginSuccess = False
    retryLoginCount = 0
    global db_settings

    # 登入系統與Log紀錄
    while True:
        clearConsole()
        print("[*]========================================")
        print("[*]" + "粉鳥旅行社會員資料庫管理系統".center(25))
        print("[*]========================================")
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
            login_threading = threading.Thread(target=connect_sql_server)
            login_threading.start()

            # 2021.09.04 updated
            login_start_time = datetime.datetime.now()
            timeout = 60
            timeout_check = True
            is_exit = False
            retryLogin = ''
            while True:
                print(f"[-]連接至資料庫 -> {db_settings['database']} 中, 路徑為: {db_settings['host']}:{db_settings['port']}")
                
                for step in track(range(300), description="[\]連線中...", ):
                    login_end_time = datetime.datetime.now()
                    
                    if login_threading.is_alive():
                        time.sleep(0.05)
                    else:
                        pass

                    if (login_end_time - login_start_time).seconds > timeout:
                        raise TimeoutError
                
                if not login_threading.is_alive():
                    break
            
            loginTime = datetime.datetime.now()
            login_threading.join()   
            
            if not loginSuccess:
                if is_IP_allow:
                    raise pymysql.err.OperationalError
                else:
                    raise pymysql.err.InternalError
            print(f"[*]資料庫: {db_settings['database']} 連線成功!")
            loginSuccess = True
            timeout_check = False
            break
        except pymysql.err.OperationalError:
            print(f"[!]第 {retryLoginCount+1} 次嘗試登入失敗")
            if retryLoginCount > 0:
                print("[!](看到這段訊息代表你嘗試登入失敗一次以上)如果確認帳號密碼輸入無錯誤，可能是網路連線上的設定問題，請連絡相關人員設定")
            retryLogin = input("[!]帳號或密碼有錯，請問是否要重新輸入，否則系統自動關閉(Y/N): ")
            loginSuccess = False
            timeout_check = False
        except pymysql.err.InternalError:
            print('[!]' + '此電腦的 IP 不在資料庫允許的連線清單內，請將IP加入允許連線清單後再重新登入。')
            input('[!]' + '請按Enter來結束程式...')
            sys.exit()
        except TimeoutError:
            print("[!]連線逾時... 請檢查網路相關設定 !")
            # <----- Write Login Log start ----->
            configBasePath = f"{os.getcwd()}\\登入紀錄"
            configPath = (
                configBasePath + "\\" + f"{login_start_time.strftime('%Y-%m')}月份-登入紀錄.ini"
            )
            if not os.path.isdir(configBasePath):
                os.mkdir(configBasePath)

            if not config.check_config_if_exist(configPath):
                config.make_config(configPath, configMode=2)

            loginLog = f"{login_start_time}\t{db_settings['user']}\t{'連線逾時'}\n"
            config.write_config(path=configPath, content=loginLog)
            # <----- Write Login Log end ----->
            sys.exit()        
        finally:
            msg_loginFail = f'第 {retryLoginCount+1} 次嘗試登入失敗'
            if retryLogin in ("y", "Y"):
                retryLoginCount += 1
            elif retryLogin in ('n', 'N'):
                is_exit = True
            else:
                pass

            if not timeout_check:
                # 連線逾時的狀況下 loginTime is undefine
                # <----- Write Login Log start ----->
                writeLog(
                    is_Success=loginSuccess,
                    connect=conn_log,
                    writeList='LOGIN_LOG',
                    key=('時間', '操作者', '狀態'),
                    value_success=(
                        f'{loginTime.strftime("%Y-%m-%d %H:%M:%S")}',
                        db_settings['user'],
                        '登入成功' 
                    ),
                    value_failed=(
                        f'{loginTime.strftime("%Y-%m-%d %H:%M:%S")}',
                        db_settings['user'],
                        msg_loginFail
                    ),
                    is_commit=True
                )
                # <----- Write Login Log end ----->
            if is_exit:
                exit_pinkbird_system()

    # <----- Get Column Name start ----->
    corsor = conn.cursor()
    corsor.execute(getColumeNames(tableName='會員資料'))
    columeNames = [colName[0] for colName in corsor.fetchall()]
    global column_Dict
    column_Dict = dict(zip(
        [str(int(idx[0]) + 1) for idx in enumerate(columeNames)],
        [key for key in columeNames]
    ))
        # column_Dict will be like below
        # column_Dict = {
        #     '1': '姓名', 
        #     '2': '身分證字號', 
        #     '3': '生日', 
        #     '4': '電話', 
        #     '5': '餐食', 
        #     '6': '特殊需求', 
        #     '7': '暱稱', 
        #     '8': '旅遊天數', 
        #     '9': '身心障礙'
        # }
    # <----- Get Column Name End ----->
    try:
        dataRepeatCheck()
    except KeyboardInterrupt:
        print('\n\n\n[!]已取消重複會員資料處理！ 操作會員資料與出團時務必注意是否使用到重複的資料！')

    # <----- Main Loop start ----->
    while True:
        print("[*]========================================")
        print("[*]" + "粉鳥旅行社會員資料庫管理系統".center(25))
        print("[*]========================================")
        print(f'[*]目前登入身分為: {db_settings["user"]}')
        print(f'[*]登入時間為: {loginTime.strftime("%Y-%m-%d %H:%M:%S")}')
        print("[*]" + "================功能選項================")
        print("[*]" + "\t  1. 產生出團名冊")
        print("[*]" + "\t  2. 旅遊金序號管理")
        print("[*]" + "\t  3. 會員資料查詢")
        print("[*]" + "\t  4. 新增會員資料")
        print("[*]" + "\t  5. 開啟網頁介面")
        print("[*]" + "\t  6. 資料庫總覽")
        print("[*]" + "\t  7. 會員資料總覽")
        print("[*]" + "\t  e. 離開系統")
        print("[*]" + "=" * 40)
        print("[*]在各功能介面中，隨時可以按下「Ctrl + C」回到此主選單介面")
        functionChoose = input(f"[?]請選擇功能: ")
        if functionChoose == 'E':
            functionChoose == 'e'

        if functionChoose not in functionDefined:
            print("[*]===============================================")
            input("[?]請重新輸入功能選單中之數字...")
            clearConsole()
            continue

        try:
            # <----- Write Operation Log start ----->
            if functionChoose == "1":
                operationName_inChinese = "產生出團名冊"
            elif functionChoose == "2":
                operationName_inChinese = "旅遊金序號管理"
            elif functionChoose == "3":
                operationName_inChinese = "會員資料(可查詢、編輯或刪除)"
            elif functionChoose == "4":
                operationName_inChinese = "手動新增會員資料"
            # elif functionChoose == "5":
            #     operationName_inChinese = "檢查會員資料是否重複"
            elif functionChoose == "5":
                operationName_inChinese = "開啟網頁版管理介面"
            elif functionChoose == "6":
                operationName_inChinese = "資料庫總覽"
            elif functionChoose == "7":
                operationName_inChinese = "查看所有會員資料（總覽）"
            # elif functionChoose == "i":
            #     operationName_inChinese = "開啟GitHub"
            elif functionChoose == 'e':
                operationName_inChinese = "結束系統"
            else:
                operationName_inChinese = functionChoose

            # <----- Write Operation Log start ----->
            writeOperationLog(
                connect=conn_log,
                user=db_settings["user"],
                content=operationName_inChinese
            )
            # <----- Write Operation Log end ----->

            pinkbird_function(functionChoose, functionName=operationName_inChinese)
        except Endding:
            totalTime = str(datetime.datetime.now()-loginTime).split(':')
            totalTime = f'{totalTime[0]}:{totalTime[1]}:{totalTime[2].split(".")[0]}'
            writeLog(
                is_Success=True,
                connect=conn_log,
                writeList='LOGIN_LOG',
                key=('時間', '使用者', '內容'),
                value_success=(
                    f'{loginTime.strftime("%Y-%m-%d %H:%M:%S")}',
                    db_settings['user'],
                    f'結束系統 總運行時間: {totalTime}' 
                ),
                value_failed=(
                    f'{loginTime.strftime("%Y-%m-%d %H:%M:%S")}',
                    db_settings['user'],
                    f'結束系統 總運行時間: {datetime.datetime.now()-loginTime}'
                ),
                is_commit=True
            )
            sys.exit()
        except KeyboardInterrupt:
            print("\n[*]系統將回到主選單")
        finally:
            try:
                if operationName_inChinese == "結束系統":
                    input("[*]請按「Enter鍵」來結束程式...")
                else:
                    input("[*]請按「Enter鍵」以繼續...")
            except KeyboardInterrupt:
                pass
            # 結束每階段任務後清除 Console
            clearConsole()
    # <----- Main Loop end ----->
