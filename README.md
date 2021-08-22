# Pinkbird-Client-Management-System

<img src = 'https://user-images.githubusercontent.com/34447298/130364293-bb9d9f77-2397-4571-98cd-894ca79139e0.png' height=50% width=50%></img>
<img src = 'https://user-images.githubusercontent.com/34447298/130364251-8e9b2dfb-299b-42f1-865a-1b8397831891.png' height=25% width=25%></img>

透過 Python 以及 MySQL 設計之企業客戶資料庫管理系統

## 功能

 - 產生出團名冊
 - 產生折扣碼
 - 編輯會員資料(包含查詢以及刪除)
 - 手動新增會員資料
 - 檢查會員資料是否重複

## 使用說明

 - Config配置
 
第一次運行時系統會自動建立config.ini<br>
需先至運行目錄下配置Config.ini相關內容才能運行<br>
詳細說明於config.ini中有說明
 
 - Database配置

請先確認 MySQL 的 Server 端有啟動TCP/IP連線<br>
並請確認 PORT 沒有問題

 - 登入帳號權限

MySQL 的 Server 端對於登入帳號的權限設定也請留意<br>
確保連線的IP的連線允許，如有防火牆也請將連線IP寫入防火牆規則
