import configparser
import os

# """
# [Synology]
# path = 
# port = 
#
# [Log]
# user = 
# password = 
# database = 
# """

def check_config_if_exist(path):
    return bool(os.path.isfile(path))


def load_config(path = "./config.ini"):
    config = configparser.ConfigParser()    
    config.read(path, encoding="utf-8")

    return {
        "host": config["Setting"]["host"],
        "port": config["Setting"]["port"],
        "log-user": config["Log"]["user"],
        "log-password": config["Log"]["password"],
        "log-database": config["Log"]["database"]
    }


def make_config(path: str, configMode: int):
    """
     - configMode == 1: make config of 'system setting'
     - configMode == 2: make config of 'login log '
     - configMode == 3: make config of 'operation log '
    """
    if configMode == 1:        
        with open(path, "w", encoding="utf-8") as f:
            system_config(f)
    elif configMode == 2:
        with open(path, "w", encoding="utf-8") as f:
            login_log_config(f)
    elif configMode == 3:
        with open(path, "w", encoding="utf-8") as f:
            operationLog_config(f)
    else:
        print("[!]config.py 中 make_config 函數之參數 configMode 設定錯誤")


def write_config(path, content):
    with open(path, "a", encoding="utf-8") as f:
        f.write(content)


def system_config(f):
    f.write("[Setting]\n")
    f.write("; host 為資料庫所在位置\n")
    f.write("host = \n")
    f.write("; port 為資料庫所對應之 IP 的連接埠\n")
    f.write("port = ")
    f.write("\n\n[Log]\n")
    f.write("user = \n")
    f.write("password = \n")
    f.write("database = \n")

def login_log_config(f):
    f.write("[粉鳥旅行社會員資料庫管理系統 登入紀錄]\n")
    f.write("       時間	             操作者		 狀態\n")

def operationLog_config(f):
    f.write("[粉鳥旅行社會員資料庫管理系統 操作紀錄]\n")
    f.write("       時間	             操作者		 內容\n")