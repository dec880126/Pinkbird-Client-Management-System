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