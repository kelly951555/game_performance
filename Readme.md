chromedriver version
----
94.0.4606.61

使用說明
----
1. `game_performance_Slot.exe` 需與 `chromedriver.exe` 放在同一層
2. 必要參數
   1. 代理商
   2. 遊戲編號
   3. 日期
3. 執行完成會產生 `代理商_遊戲編號_日期.csv`
4. 資料來源: `https://dev-admin-br-02.iplaystar.net/`

參數說明
----
### 代理商規格
1. 字數<7 `EX. test-7`
   1. 會將英文轉換大寫，去掉- `EX. TEST7`
2. 其他會依照輸入不轉型防呆 `EX. Test-MultiHost-2`

### 遊戲編號規格
1. 防呆只有將空格去除以及轉換大寫

### 日期規格
1. 指定格式 `YYYY-MM-DD`
2. 超出規範會轉為當天日期，反之當日可以不用輸入日期

輸出檔案說明
----
1. 內容
   1. 顯示 遊戲編號、代理商
   2. List of History → 歷史紀錄抓取的資料列表
   3. Sum by Player → 依照 `List of History` 抽出玩家資料計算
   4. Sum of History → 依照 `List of History` 的全部資料計算績效需要的值
   5. Comparison Result → 自動比對 `遊戲績效-遊戲`
2. 例外情形
   1. 以下情形 CSV 內容會顯示 `no_data`
      1. 網站掛掉
      2. 登入失敗
      3. 遊戲紀錄頁掛掉
      4. 沒有遊戲紀錄
   2. 遊戲績效掛掉 `Comparison Result` 會顯示 `performance does not exist`
   3. 遊戲績效沒資料會抓到0，與第2點不同

流程圖
----
![流程圖](D:\project\game_performance\流程圖.png)