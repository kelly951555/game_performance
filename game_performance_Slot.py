import pandas as pd
from inspection import *
import configparser
import os

fp_dir = os.path.dirname(__file__)
config_path = os.path.join(fp_dir, "config.ini")
config = configparser.ConfigParser()
config.read(config_path)
url = config['backstage']['url']
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
# 日期格式錯誤換今天
if not is_valid_date(date_time):
    date_time = today
else:
    date_time = date_time
login_status = login(url, username, user_password)
if login_status != 'login successfully':
    print(login_status)
    logout()
else:
    history_status = get_history(url, date_time, agent_value, g_id, 'slot')
    performance_status = get_performance(url, date_time, agent_value, g_id, 'slot')
    logout()
    print('---遊戲紀錄計算中---')
    filename = './{}_{}_{}.csv'.format(agent_value, g_id, date_time)
    info = pd.DataFrame({'Game ID': g_id, 'Agent': agent_value}, index=[1])
    skip = pd.DataFrame()
    if len(history_status) != 1:
        print('無遊戲紀錄')
        print('---製作報表 {}---'.format(filename))
        no_data = pd.DataFrame({'no_data': history_status}, index=[1])
        info.to_csv(filename, encoding='utf-8', index=False)
        skip.to_csv(filename, encoding='utf-8', index=False, mode='a')
        no_data.to_csv(filename, encoding='utf-8', index=False, header=False, mode='a')
        print('完成報表 {}'.format(filename))
    else:
        # <!----List of History----
        # 過濾主單class="img_div"
        result = history_status.find_all("div", {'class': 'img_div'})
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
            for p in history_status.select(
                    "#history > div:nth-child({}) > div > table > tbody > tr:nth-child(4) > td".format(r)):
                # 玩家名稱去除代理商
                player = p.text.strip().split(')')[1].replace(' ', '')
            # 序號SN、面額Denom、帳戶Credit、押注Bet
            for tr in history_status.select(
                    "#history > div:nth-child({}) > div > table > tbody > tr:nth-child(10)".format(r)):
                row1 = [td.text.replace('\n', '').replace('\xa0', '').replace(',', '') for td in tr.find_all('td')]
                # str to float, skip SN
                for i in range(1, len(row1)):
                    row1[i] = float(row1[i])
            # 彩金Jackpot、贏分Win、免遊贏分Bonus Win
            for tr2 in history_status.select(
                    "#history > div:nth-child({}) > div > table > tbody > tr:nth-child(12)".format(r)):
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
        rtp = round(total_win / sum_Bet * 100, 2)
        avg_bet = round(sum_Bet / len(number_list), 2)
        players_count = round(len(df.groupby(['Player']).SN.nunique()), 2)
        net = round(sum_Bet - total_win, 2)
        rtp_t = '{}%'.format(rtp)
        total_columns = ['Game ID', 'Coin In', 'Coin Out', 'Bonus',
                         'Jackpot', 'Net Win', 'R.T.P', 'avg Bet', 'Total Games', 'People']
        total_row = [g_id, sum_Bet, total_win, sum_Bonus_Win, sum_Jackpot, net, rtp_t, avg_bet, len(number_list),
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
        for Player in df['Player'].unique():
            Bet = float(p_s.loc[Player, 'Bet'])
            Jackpot = float(p_s.loc[Player, 'Jackpot'])
            Win = float(p_s.loc[Player, 'Win'])
            BonusWin = float(p_s.loc[Player, 'Bonus Win'])
            Game = player_count[Player]
            Coin_in = round(Bet, 2)
            Coin_out = round(Win + BonusWin, 2)
            Bonus = round(BonusWin, 2)
            Jackpot = round(Jackpot, 2)
            NetWin = round(Coin_in - Coin_out, 2)
            RTP = '{}%'.format(round(Coin_out / Coin_in * 100, 2))
            Avg = round(Coin_in / Game, 2)
            p_row.append([Player, Coin_in, Coin_out, Bonus, Jackpot, NetWin, RTP, Avg, Game])
        player_df = pd.DataFrame(data=p_row, columns=p_column)
        player_df.sort_values(['Player'], ascending=True)
        # ----Sum by Player----!>
        print('遊戲紀錄計算完成')
        # <!----Comparison Result----
        # if performance_status != 'load game_performance failed' or 'enter game_performance failed':
        if isinstance(performance_status, list):
            print('---比對遊戲績效---')
            cp_list = ['Coin In', 'Coin Out', 'Bonus', 'Jackpot', 'Net Win', 'R.T.P', 'avg Bet', 'Total Games',
                       'People']
            cp_columns = ['Item', 'History', 'Performance', 'Result']
            total_list = total.values.tolist()[0]
            cp_rows = list()
            cp_rows.append(comparison(cp_list[0], total_list[1], performance_status[0]))
            cp_rows.append(comparison(cp_list[1], total_list[2], performance_status[1]))
            cp_rows.append(comparison(cp_list[2], total_list[3], performance_status[2]))
            cp_rows.append(comparison(cp_list[3], total_list[4], performance_status[3]))
            cp_rows.append(comparison(cp_list[4], total_list[5], performance_status[4]))
            RTP_p1 = performance_status[5].split('%')[0]
            t6 = total_list[6].split('%')[0]
            if float(t6) == float(RTP_p1):
                r6 = [cp_list[5], total_list[6], performance_status[5], '[PASS]']
            else:
                r6 = [cp_list[5], total_list[6], performance_status[5], '[FAIL]']
            cp_rows.append(r6)
            cp_rows.append(comparison(cp_list[6], total_list[7], performance_status[6]))
            cp_rows.append(comparison(cp_list[7], total_list[8], performance_status[7]))
            cp_rows.append(comparison(cp_list[8], total_list[9], performance_status[8]))
            print('比對完成')
            cp = pd.DataFrame(data=cp_rows, columns=cp_columns)
        else:
            cp = pd.DataFrame({'no_data': performance_status}, index=[1])
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

os.system("pause")
