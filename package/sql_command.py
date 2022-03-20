"""
FUNCTION LIBRARY OF SQL COMMAND

 - searchCommand
 - searchCommand_sp
 - listAllCommand
 - deleteCommand
 - insertCommand
 - editCommand
 - countCommand
"""
from pymysql.connections import Connection
import datetime


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
    value = tuple([str(x) for x in value])
    singleQuote = "\'"
    backQuote = "`"
    return f"INSERT INTO `{str(listFrom)}` {str(key).replace(singleQuote, backQuote)} VALUES {str(value)}"

def editCommand(listFrom: str, key_toUpdate: list, value_toUpdate: list, searchBy_key: list, searchBy_value: list) -> str:
    """
    editCommand("資料表", "欲設定之欄位", "欲設定之值", "搜尋條件", "搜尋值")
     - UPDATE `資料表` SET `欲設定之欄位`= '欲設定之值' WHERE `搜尋條件` = '搜尋值';
    """
    def list_or_tuple():
        is_list = isinstance(key_toUpdate, list) and isinstance(value_toUpdate, list)
        is_tuple = isinstance(key_toUpdate, tuple) and isinstance(value_toUpdate, tuple)
        return is_list or is_tuple

    if list_or_tuple():
        result_command = ""
        for k, v in zip(key_toUpdate, value_toUpdate):
            if isinstance(v, int):
                result_command += f"UPDATE `{listFrom}` SET `{k}`={v} WHERE `{searchBy_key}`='{searchBy_value}';\n"
            if isinstance(v, str):
                result_command += f"UPDATE `{listFrom}` SET `{k}`='{v}' WHERE `{searchBy_key}`='{searchBy_value}';\n"
        return result_command
    else:
        return "UPDATE `" + str(listFrom) + "` SET `" + str(key_toUpdate) + "`='" + str(value_toUpdate) + "' WHERE `" + str(searchBy_key) + "` = '" + str(searchBy_value) + "'"

def countCommand(listfrom: str, column: str = None, value: str = None) -> str:
    """
    countCommand("資料表")
     - SELECT COUNT(*) FROM `資料表` WHERE 1

    countCommand("資料表", "欄位", "值")
     - SELECT COUNT(*) FROM `資料表` WHERE `欄位` = '值'
    """
    if column == None and value == None:
        return f"SELECT COUNT(*) FROM `{listfrom}` WHERE 1"

    return f"SELECT COUNT(*) FROM `{listfrom}` WHERE `{column}` = '{str(value)}'"

def searchCommand_sp(listfrom: str, column: str = None, condition_col: str = None, condition_value: str = None) -> str:
    """
    searchCommand_sp("資料表", "欄位")
     - SELECT `欄位` FROM `資料表` WHERE 1

    searchCommand_sp("資料表", "欄位", "條件欄位", "條件值")
     - SELECT `欄位` FROM `資料表` WHERE `條件欄位` = '條件值'
    """
    if condition_col == None and condition_value == None:
        return f"SELECT `{column}` FROM `{listfrom}` WHERE 1"

    return f"SELECT `{column}` FROM `{listfrom}` WHERE `{condition_col}` = '{str(condition_value)}'"

def getColumeNames(tableName: str):
    return f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '{tableName}'"

def sql_operator(connect: Connection, instruction: str, is_fetchAll: bool = False, is_commit: bool = False) -> tuple:
    editor = connect.cursor()
    editor.execute(instruction)

    if is_commit:
        connect.commit()

    if is_fetchAll:
        return editor.fetchall()
    else:
        return editor.fetchone()

def writeLog(is_Success: bool, connect: Connection, writeList: str, key: tuple, value_success: tuple, value_failed: tuple,is_commit: bool = False):
    if is_Success:
        sql_operator(
            connect=connect,
            instruction=insertCommand(
                listFrom=writeList,
                key=('時間', '操作者', '內容'),
                value=value_success
            ),
            is_commit=is_commit
        )
    else:
        sql_operator(
            connect=connect,
            instruction=insertCommand(
                listFrom=writeList,
                key=('時間', '操作者', '內容'),
                value=value_failed
            ),
            is_commit=is_commit
        )

def writeOperationLog(connect: Connection, user: str, content: str):
    """
    ### 參數用法

     - value(
         時間,
         操作者,
         內容
     )
    """
    sql_operator(
        connect=connect,
        instruction=insertCommand(
            listFrom='OP_LOG',
            key=('時間', '操作者', '內容'),
            value=(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), user, content)
        ),
        is_commit=True
    )

def writeTravelLog(connect: Connection, date: str, groupName: str, days: int, costs: list, attends: list):
    """
    ### 參數用法

     - date: 出團日期
     - groupName: 團名
     - days: 日數
     - costs: 團費
     - attends: 參加者清單
    """
    SN_base = date.replace('.', '')

    check = sql_operator(
        connect=connect,
        instruction=searchCommand(
            listFrom='DEPART_LOG',
            key='S/N',
            searchBy=SN_base + '01'
        ),
        is_fetchAll=True
    )
    if len(check) == 0:
        serialNumber = SN_base + '01'
    else:
        serialNumber = SN_base + f'{len(check)+1:02d}'

    data = {
        'S/N': serialNumber,
        '日期': date,
        '團名': groupName,
        '日數': str(days),
        '團費': str(costs),
        '參加者清單': str(attends)
    }

    sql_operator(
        connect=connect,
        instruction=insertCommand('DEPART_LOG', tuple(data.keys()), tuple(data.values())),
        is_commit=True
    )
