SELECT * FROM `會員資料` WHERE '身分證字號' = '~~';

SELECT * FROM `會員資料`;

DELETE FROM `會員資料` WHERE '姓名' = '王小明';

INSERT INTO `會員資料` (`姓名`, `身分證字號`, `生日`, `電話`, `餐食`, `特殊需求`, `暱稱`, `旅遊天數`) VALUES ([value-1],[value-2],[value-3],[value-4],[value-5],[value-6],[value-7],[value-8]);

UPDATE `旅遊金序號` SET `是否使用過`=0 WHERE `序號` = '120288878ZJtKV';

select * from `會員資料` group by `身分證字號` having count(*) > 1;
