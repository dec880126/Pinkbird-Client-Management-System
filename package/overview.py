from pymysql.connections import Connection
from package.sql_command import countCommand, searchCommand_sp
from package.year_cal import get_years_old
import datetime

def travelsDay_ranking_overview(connection: Connection):
    with connection.cursor() as cur:
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

    with connection.cursor() as cur:
        command = "SELECT `姓名`, `旅遊天數` FROM `會員資料` ORDER BY `會員資料`.`旅遊天數` DESC LIMIT " + str(topNums)
        cur.execute(command)
        leaderboard = cur.fetchall()

    print("[*]" + "="*40)
    for idx, ranking in enumerate(leaderboard):
        print(f"[>]第{idx+1:3d} 名: {ranking[0]:4s} 共參加了 {ranking[1]:4d} 天旅遊行程")
    print("[*]" + "="*40)
    print(f"[*]資料庫總人數為 {amount_of_clients} 人")


def ages_overview(connection: Connection):
    age_0_3 = age_4_6 = age_7_12 = age_13_64 = age_65up = undefined = 0
    total_age = 0

    with connection.cursor() as cur:
        cur.execute(countCommand("會員資料"))
        amount_of_clients = cur.fetchone()[0]
        cur.execute(searchCommand_sp("會員資料", "生日"))
        births = cur.fetchall()
        for birth in births:
            age = get_years_old(birth[0], datetime.date.today())

            if age >= 0:
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
            elif age < 0:
                undefined += 1
        
    print("[*]" + "="*40)
    print(f"[*] 0  ~ 3   歲共有 {age_0_3} 人    -> {age_0_3/amount_of_clients*100: 3.2f}%")
    print(f"[*] 4  ~ 6   歲共有 {age_4_6} 人    -> {age_4_6/amount_of_clients*100: 3.2f}%")
    print(f"[*] 7  ~ 12  歲共有 {age_7_12} 人    -> {age_7_12/amount_of_clients*100: 3.2f}%")
    print(f"[*] 13 ~ 64  歲共有 {age_13_64} 人    -> {age_13_64/amount_of_clients*100: 3.2f}%")
    print(f"[*]   >= 65  歲共有 {age_65up} 人    -> {age_65up/amount_of_clients*100: 3.2f}%")
    print(f"[*]  無資料     共有 {undefined} 人    -> {undefined/amount_of_clients*100: 3.2f}%")
    print("[*]" + "="*40)
    print(f"[*]資料庫總人數為 {amount_of_clients} 人，平均 {total_age/(amount_of_clients - undefined): 2.2f} 歲")


def foodType_overview(connection: Connection):
    with connection.cursor() as cur:
        cur.execute(countCommand("會員資料"))
        amount_of_clients = cur.fetchone()[0]
        cur.execute(countCommand("會員資料", "餐食", "葷食"))
        meatfood = cur.fetchone()[0]
        cur.execute(countCommand("會員資料", "餐食", "素食"))
        vegetarian = cur.fetchone()[0]
    
    print("[*]" + "="*40)
    print(f"[*]餐食為「素食」者共有 {vegetarian} 人    -> {vegetarian/amount_of_clients*100: 3.2f}%")
    print(f"[*]餐食為「葷食」者共有 {meatfood} 人    -> {meatfood/amount_of_clients*100: 3.2f}%")
    print("[*]" + "="*40)
    print(f"[*]資料庫總人數為 {amount_of_clients} 人")


def disability_overview(connection: Connection, database: str):
    command_base = "SELECT COUNT(*) FROM `會員資料` WHERE `身心障礙` LIKE "
    with connection.cursor() as cur:
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
    print(f"[*]資料庫: {database} 的 {amount_of_clients} 名會員中共有 {disability_amount} 人領有身心障礙手冊\n[*]分別為: ")
    print(f"[*]    輕度: {disability_level_1} 人")
    print(f"[*]    中度: {disability_level_2} 人")
    print(f"[*]    重度: {disability_level_3} 人")
    if disability_level_1 + disability_level_2 + disability_level_3 != disability_amount:
        unlabeled = disability_amount - (disability_level_1 + disability_level_2 + disability_level_3)
        print(f"[*]    未登記: {unlabeled} 人")
    print("[*]" + "="*40)
    print(f"[*]資料庫總人數為 {amount_of_clients} 人")


def discountCode_overview(connection: Connection):
    with connection.cursor() as cur:
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