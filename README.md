# Pinkbird-Client-Management-System

<img src = 'https://user-images.githubusercontent.com/34447298/130364293-bb9d9f77-2397-4571-98cd-894ca79139e0.png' height=50% width=50%></img>
<img src = 'https://user-images.githubusercontent.com/34447298/130364251-8e9b2dfb-299b-42f1-865a-1b8397831891.png' height=25% width=25%></img>

透過 Python 以及 MySQL 設計之企業客戶資料庫管理系統
 
 - [PCMS使用說明書下載](https://github.com/dec880126/Pinkbird-Client-Management-System/releases/download/5.6.3/PCMS.UG2111.2.pdf)



   <a href = "https://github.com/dec880126/Pinkbird-Client-Management-System/blob/main/LICENSE"><img alt="GitHub" src="https://img.shields.io/github/license/dec880126/Pinkbird-Client-Management-System?style=plastic"></a>
   <a href = "https://github.com/dec880126/Pinkbird-Client-Management-System/releases/tag/6.1.1"><img alt="GitHub release (latest by date)" src="https://img.shields.io/github/downloads/dec880126/Pinkbird-Client-Management-System/latest/total?style=plastic"></a>

## 目錄

* [功能](#function)
* [操作介面](#interface)
* [常見問題](#problems)
    * [Config配置](#config)
    * [Database配置](#database)
    * [登入帳號權限](#user)
    * [登入與操作紀錄](#log)
* [版權聲明](#copyright)

## 最新版本: 6.1.1

> Last update: 2022.02.25
### What's New in v6.1.1

 - Update set_cost() function
 - Optimization WorkFlow
 - Fixed the bug about age analysis
 - Add some scripts for run and compile to .exe


## To-Do List
 - [x] Solve bugs in v5.7.0-dev
 - [x] Record operation log in SQL Server
 - [ ] Automatically Backup solution for SQL Server in Python


## <a id="interface">操作介面</a>
 - 登入畫面

於此處輸入MySQL Server之具存取權限之使用者資訊。 (詳細的登入資訊請參照: [Config配置](#config))

<img src = 'https://user-images.githubusercontent.com/34447298/130611339-8991e82a-6ab1-429a-9f80-590732d6a8d4.png' height=75% width=75%></img>

 - 主選單畫面介面

此處可選擇進入各項功能介面中，進入功能介面後也可透過鍵盤操作 `Ctrl+C` 來回到此介面。

<img src = 'https://user-images.githubusercontent.com/34447298/130611391-2692c5d2-f6d0-4e42-8ecb-f043633fbddf.png' height=75% width=75%></img>

 - 產生出團名冊

可進入介面並選擇指定模式後，輸入報名格式的 .XLSX 檔後，系統將會自動向SQL Server請求會員詳細資料，並分析處理後回傳，並輸出一份清晰的Excel檔。

<img src = 'https://user-images.githubusercontent.com/34447298/130611415-02a9a237-3c26-4a87-be9f-5b4ea4b2b3f0.png' height=75% width=75%></img>

 - 折扣碼管理

提供兩種模式的折扣碼產生功能，以及後續的折扣碼管理功能。

<img src = 'https://user-images.githubusercontent.com/34447298/130611438-1d233a46-b681-4873-8ade-598046812a94.png' height=75% width=75%></img>

 - 編輯使用者資料

將複雜的 SQL 指令設計成簡單的中文化使用者介面，可輕鬆操作 MySQL 系統

<img src = 'https://user-images.githubusercontent.com/34447298/130611455-d25193ad-bd46-49e8-a1a6-2f340fb075e6.png' height=75% width=75%></img>

 - 新增使用者資料

如有新增單筆使用者資料需求，可使用此功能來達到快速且方便的新增資料功能。<br>
但是若有大量資料需要匯入，建議使用功能: 6，連入phpMyAdmin介面，選取對應Database後，尋找畫面上方的中間偏右的位置，有一項「匯入」，可一次匯入大量資料，也有支援許多格式(csv, sql...等)的匯入操作。

<img src = 'https://user-images.githubusercontent.com/34447298/130611476-bb5c675f-443b-4b97-aa39-63ae8a871223.png' height=75% width=75%></img>

 - 檢查資料庫重複度

此功能可快速檢查資料庫內是否有重複的資料存在，判斷的依據為身分證字號重複。若有存在重複項，可選取要保留的版本，最後再進行資料庫更新。

<img src = 'https://user-images.githubusercontent.com/34447298/130611492-763a4070-207e-4a7f-8ea7-fff51e8f7d5d.png' height=75% width=75%></img>

 - 開啟網頁版操作介面

選擇後系統將裕預設瀏覽器中開啟phpMyAdmin的網頁版介面。

<img src = 'https://user-images.githubusercontent.com/34447298/130611799-7c67cd9b-85b6-4282-b48f-47cf66e6ca68.png' height=75% width=75%></img>

## <a id="problems">常見問題</a>

 - <a id = "config" >Config配置</a>
 
第一次運行時系統會自動建立config.ini<br>
需先至運行目錄下配置Config.ini相關內容才能運行<br>
> host 為資料庫所在位置<br>
> port 為資料庫所對應之 IP 的連接埠
 
 - <a id="database">Database配置</a>

請先確認 MySQL 的 Server 端有啟動TCP/IP連線<br>
並請確認 PORT 沒有問題

 - <a id="user">登入帳號權限</a>

MySQL 的 Server 端對於登入帳號的權限設定也請留意<br>
確保連線的IP的連線允許，如有防火牆也請將連線IP寫入防火牆規則

 - <a id="log">登入與操作紀錄</a>

任何登入與操作的紀錄將會以.ini的格式記錄下來，保存於與程式同目錄底下的 "登入紀錄" 與 "操作紀錄" 資料夾
## <a id="copyright">版權聲明</a>

**Copyright © 2021 粉鳥旅行社 版權所有**
