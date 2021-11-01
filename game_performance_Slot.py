from bs4 import BeautifulSoup
import pandas as pd
from driver_setting import driver_init
from inspection import comparison
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
from selenium.common.exceptions import TimeoutException, WebDriverException
from datetime import date
import configparser


def is_valid_date(str_date):
    try:
        date.fromisoformat(str_date)
    except:
        return False
    else:
        return True


config = configparser.ConfigParser()
config.read('config.ini')
login = config['backstage']['url']
username = config['backstage']['user']
user_password = config['backstage']['password']
agent = input('請輸入代理商: ')
agent = agent.strip()
if len(agent) < 7:
    agent_value = agent.replace('-', '').upper()
else:
    agent_value = agent
g_id = input('請輸入遊戲編號: ')
g_id = g_id.strip().upper()
date_time = input('請輸入日期( YYYY-MM-DD ): ')
today = time.strftime("%Y-%m-%d")
# 遊戲績效-遊戲資料
performance_item = []
# 歷史紀錄 html
soup = 0
# 日期格式錯誤換今天
if not is_valid_date(date_time):
    date_time = today
else:
    date_time = date_time
driver = driver_init()
wait = WebDriverWait(driver, 3)
# 判斷網站是否存在
try:
    driver.get(login)
    # 等待登入頁
    try:
        wait_login = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="lang"]')))
        print('---登入中---')
        user_id = driver.find_element_by_id('user_id')
        password = driver.find_element_by_id('password')
        user_id.send_keys(username)
        password.send_keys(user_password)
        password.submit()
        driver.get(login + '/Player/game_history')
        print('登入完成')
        # 等待遊戲紀錄頁
        try:
            wait_history = wait.until(EC.presence_of_element_located
                                      ((By.XPATH,
                                        '//*[@id="sh_btn"]')))
            print('---遊戲紀錄擷取中---')
            # 輸入日期
            if date_time != today:
                start_history = driver.find_element_by_id('start')
                start_history.clear()
                start_history.send_keys('{} 00:00:00'.format(date_time).replace('-', '/'))
                end_history = driver.find_element_by_id('end')
                end_history.clear()
                end_history.send_keys('{} 23:59:59'.format(date_time).replace('-', '/'))

            # 筆數下拉選單
            select_count = Select(driver.find_element_by_id('count'))
            select_count.select_by_value("2000")
            # 代理商
            select_agent = Select(driver.find_element_by_id('agent'))
            select_agent.select_by_value(agent_value)
            # 選擇遊戲
            select_game = Select(driver.find_element_by_xpath('//*[@id="game_select"]'))
            # 等待遊戲列表
            time.sleep(2)
            select_game.select_by_value(g_id)
            driver.find_element_by_id('sh_btn').click()
            time.sleep(2)
            # 等待遊戲紀錄第一張圖
            try:
                wait_history = wait.until(EC.presence_of_element_located
                                          ((By.XPATH, '//*[@id="history"]/div[1]/div/table/tbody/tr[10]/td[1]')))
                print('Successfully loaded.')
                # 遊戲紀錄 html
                soup = BeautifulSoup(driver.page_source, "html.parser")
                print('遊戲紀錄擷取完成')
            except TimeoutException:
                print('load history failed')
        except TimeoutException:
            print('enter history failed')
        game_performance = login + '/Accounting/game_performance'
        driver.get(game_performance)
        try:
            wait_game_performance = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="sh_btn"]')))
            print('---遊戲績效讀取中---')
            # 輸入日期
            start_performance = driver.find_element_by_id('start')
            start_performance.clear()
            start_performance.send_keys(date_time.replace('-', '/'))
            end_performance = driver.find_element_by_id('end')
            end_performance.clear()
            end_performance.send_keys(date_time.replace('-', '/'))
            # 取消勾選 PLAYSTAR + 勾選代理商
            driver.find_element_by_xpath("//input[@value='PLAYSTAR']").click()
            driver.find_element_by_xpath("//input[@value='{}']".format(agent_value)).click()
            driver.find_element_by_xpath('//*[@id="sh_btn"]').click()
            try:
                wait_game_performance = wait.until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="DataTables_Table_1_filter"]/label/input')))
                print('Successfully loaded.')
                driver.find_element_by_xpath('//*[@id="DataTables_Table_1_filter"]/label/input').send_keys(g_id)
                time.sleep(2)
                # 遊戲績效-遊戲-老虎機列表資料
                bet_p = driver.find_element_by_xpath(
                    '//*[@id="DataTables_Table_1"]/tbody/tr/td[4]').text.strip().replace(
                    ',',
                    '')
                win_p = driver.find_element_by_xpath(
                    '//*[@id="DataTables_Table_1"]/tbody/tr/td[5]').text.strip().replace(
                    ',',
                    '')
                bonus_p = driver.find_element_by_xpath(
                    '//*[@id="DataTables_Table_1"]/tbody/tr/td[6]').text.strip().replace(
                    ',',
                    '')
                jp_p = driver.find_element_by_xpath(
                    '//*[@id="DataTables_Table_1"]/tbody/tr/td[8]').text.strip().replace(
                    ',',
                    '')
                net_p = driver.find_element_by_xpath(
                    '//*[@id="DataTables_Table_1"]/tbody/tr/td[11]').text.strip().replace(
                    ',',
                    '')
                RTP_p = driver.find_element_by_xpath(
                    '//*[@id="DataTables_Table_1"]/tbody/tr/td[12]').text.strip().replace(
                    ',',
                    '')
                avg_p = driver.find_element_by_xpath(
                    '//*[@id="DataTables_Table_1"]/tbody/tr/td[13]').text.strip().replace(
                    ',',
                    '')
                g_p = driver.find_element_by_xpath(
                    '//*[@id="DataTables_Table_1"]/tbody/tr/td[14]').text.strip().replace(
                    ',',
                    '')
                people_p = driver.find_element_by_xpath(
                    '//*[@id="DataTables_Table_1"]/tbody/tr/td[15]').text.strip().replace(
                    ',', '')
                performance_item = [bet_p, win_p, bonus_p, jp_p, net_p, RTP_p, avg_p, g_p, people_p]
                driver.quit()
                print('遊戲績效讀取完成')
            except TimeoutException:
                print('load game_performance failed')
                driver.quit()
        except TimeoutException:
            print('enter game_performance failed')
            driver.quit()
    except TimeoutException:
        print('login failed')
        driver.quit()
except WebDriverException:
    print("page down")
    driver.quit()

print('---遊戲紀錄計算中---')
filename = './{}_{}_{}.csv'.format(agent_value, g_id, date_time)
info = pd.DataFrame({'Game ID': g_id, 'Agent': agent_value}, index=[1])
skip = pd.DataFrame()
if soup == 0:
    print('無遊戲紀錄')
    print('---製作報表 {}---'.format(filename))
    no_data = pd.DataFrame({'no_data': 'no_data'}, index=[1])
    info.to_csv(filename, encoding='utf-8', index=False)
    skip.to_csv(filename, encoding='utf-8', index=False, mode='a')
    no_data.to_csv(filename, encoding='utf-8', index=False, header=False, mode='a')
    print('完成報表 {}'.format(filename))
else:
    # <!----List of History----
    # 過濾主單class="img_div"
    result = soup.find_all("div", {'class': 'img_div'})
    # 取出主單是第幾筆
    number_list = list()
    for i in result:
        for t in i.select(".number"):
            # strip去除空格
            number_list.append(t.text.strip())
    rows = list()
    row1 = []
    row2 = []
    for r in number_list:
        player = ''
        # Item、Player
        for p in soup.select("#history > div:nth-child({}) > div > table > tbody > tr:nth-child(4) > td".format(r)):
            # 玩家名稱去除代理商
            player = p.text.strip().split(')')[1].replace(' ', '')
        # 序號SN、面額Denom、帳戶Credit、押注Bet
        for tr in soup.select("#history > div:nth-child({}) > div > table > tbody > tr:nth-child(10)".format(r)):
            row1 = [td.text.replace('\n', '').replace('\xa0', '').replace(',', '') for td in tr.find_all('td')]
            # str to float, skip SN
            for i in range(1, len(row1)):
                row1[i] = float(row1[i])
        # 彩金Jackpot、贏分Win、免遊贏分Bonus Win
        for tr2 in soup.select("#history > div:nth-child({}) > div > table > tbody > tr:nth-child(12)".format(r)):
            row2 = [td.text.replace('\n', '').replace('\xa0', '').replace(',', '') for td in tr2.find_all('td')]
            # str to float, skip SN
            row2 = list(map(float, row2))
        rows.append([r, player] + row1 + row2)

    # '項目', '序號', '面額', '帳戶', '押注', '彩金', '贏分', '免遊贏分'
    columns = ['Item', 'Player', 'SN', 'Denom', 'Credit', 'Bet', 'Jackpot', 'Win', 'Bonus Win']
    df = pd.DataFrame(data=rows, columns=columns)
    # ----List of History----!>
    # <!----Sum of History-----
    sum_Bet = round(df['Bet'].sum(), 2)
    sum_Jackpot = round(df['Jackpot'].sum(), 2)
    sum_Win = round(df['Win'].sum(), 2)
    sum_Bonus_Win = round(df['Bonus Win'].sum(), 2)
    total_win = round(sum_Win + sum_Bonus_Win, 2)
    RTP = round(total_win / sum_Bet * 100, 2)
    AVG_BET = round(sum_Bet / len(number_list), 2)
    players_count = round(len(df.groupby(['Player']).SN.nunique()), 2)
    net = round(sum_Bet - total_win, 2)
    RTP_t = '{}%'.format(RTP)
    total_columns = ['Game ID', 'Coin In', 'Coin Out', 'Bonus',
                     'Jackpot', 'Net Win', 'R.T.P', 'avg Bet', 'Total Games', 'People']
    total_row = [g_id, sum_Bet, total_win, sum_Bonus_Win, sum_Jackpot, net, RTP_t, AVG_BET, len(number_list),
                 players_count]
    total = pd.DataFrame(data=[total_row], columns=total_columns)
    # ----Sum of History-----!>
    # <!----Sum by Player----
    # 計算各玩家出現次數(series)
    player_count = df['Player'].value_counts()
    # 玩家列表
    players = df['Player'].unique()
    p_s = df.groupby(['Player']).agg({'Bet': 'sum', 'Jackpot': 'sum', 'Win': 'sum', 'Bonus Win': 'sum'})
    p_column = ['Player', 'Coin In', 'Coin Out', 'Bonus', 'Jackpot', 'Net Win', 'R.T.P', 'avg Bet', 'Total Games']
    p_row = list()
    for p in df['Player'].unique():
        Bet = float(p_s.loc[p, 'Bet'])
        Jackpot = float(p_s.loc[p, 'Jackpot'])
        Win = float(p_s.loc[p, 'Win'])
        BonusWin = float(p_s.loc[p, 'Bonus Win'])
        game = player_count[p]
        coin_in = round(Bet, 2)
        coin_out = round(Win + BonusWin, 2)
        Bonus = round(BonusWin, 2)
        Jackpot = round(Jackpot, 2)
        NetWin = round(coin_in - coin_out, 2)
        RTP = '{}%'.format(round(coin_out / coin_in * 100, 2))
        avg = round(coin_in / game, 2)
        p_row.append([p, coin_in, coin_out, Bonus, Jackpot, NetWin, RTP, avg, game])
    player_df = pd.DataFrame(data=p_row, columns=p_column)
    player_df.sort_values(['Player'], ascending=True)
    # ----Sum by Player----!>
    print('遊戲紀錄計算完成')
    # <!----Comparison Result----
    if len(performance_item) > 0:
        print('---比對遊戲績效---')
        cp_list = ['Coin In', 'Coin Out', 'Bonus', 'Jackpot', 'Net Win', 'R.T.P', 'avg Bet', 'Total Games', 'People']
        cp_columns = ['Item', 'History', 'Performance', 'Result']
        total_list = total.values.tolist()[0]
        cp_rows = list()
        cp_rows.append(comparison(cp_list[0], total_list[1], performance_item[0]))
        cp_rows.append(comparison(cp_list[1], total_list[2], performance_item[1]))
        cp_rows.append(comparison(cp_list[2], total_list[3], performance_item[2]))
        cp_rows.append(comparison(cp_list[3], total_list[4], performance_item[3]))
        cp_rows.append(comparison(cp_list[4], total_list[5], performance_item[4]))
        RTP_p1 = performance_item[5].split('%')[0]
        t6 = total_list[6].split('%')[0]
        if float(t6) == float(RTP_p1):
            r6 = [cp_list[5], total_list[6], performance_item[5], '[PASS]']
        else:
            r6 = [cp_list[5], total_list[6], performance_item[5], '[FAIL]']
        cp_rows.append(r6)
        cp_rows.append(comparison(cp_list[6], total_list[7], performance_item[6]))
        cp_rows.append(comparison(cp_list[7], total_list[8], performance_item[7]))
        cp_rows.append(comparison(cp_list[8], total_list[9], performance_item[8]))
        print('比對完成')
        cp = pd.DataFrame(data=cp_rows, columns=cp_columns)
    else:
        cp = pd.DataFrame({'no_data': 'performance does not exist'}, index=[1])
    # ----Comparison Result----!>
    info = pd.DataFrame({'Game ID': g_id, 'Agent': agent_value}, index=[1])
    skip = pd.DataFrame()
    history_list = pd.DataFrame({'history_sum': 'List of History'}, index=[1])
    player_sum = pd.DataFrame({'player_sum': 'Sum by Player'}, index=[1])
    history_sum = pd.DataFrame({'history_sum': 'Sum of History'}, index=[1])
    Comparison_result = pd.DataFrame({'Comparison_result': 'Comparison Result'}, index=[1])
    print('---製作報表 {}---'.format(filename))
    info.to_csv(filename, encoding='utf-8', index=False)
    skip.to_csv(filename, encoding='utf-8', index=False, mode='a')
    history_list.to_csv(filename, encoding='utf-8', index=False, header=False, mode='a')
    df.to_csv(filename, encoding='utf-8', index=False, mode='a')
    skip.to_csv(filename, encoding='utf-8', index=False, mode='a')
    player_sum.to_csv(filename, encoding='utf-8', index=False, header=False, mode='a')
    player_df.to_csv(filename, encoding='utf-8', index=False, mode='a')
    skip.to_csv(filename, encoding='utf-8', index=False, mode='a')
    history_sum.to_csv(filename, encoding='utf-8', index=False, header=False, mode='a')
    total.to_csv(filename, encoding='utf-8', index=False, mode='a')
    skip.to_csv(filename, encoding='utf-8', index=False, mode='a')
    Comparison_result.to_csv(filename, encoding='utf-8', index=False, header=False, mode='a')
    cp.to_csv(filename, encoding='utf-8', index=False, mode='a')
    print('完成報表 {}'.format(filename))
