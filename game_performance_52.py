import sys
import pandas as pd
from bs4 import BeautifulSoup
from inspection import *
import configparser
import os
import pathlib

room_index = {'Fun Room': 0, 'Bronze Room': 1, 'Silver Room': 2, 'Gold Room': 3, 'Ruby Room': 4, 'Diamond Room': 5}
fp_dir = pathlib.Path().absolute()
config_path = os.path.join(fp_dir, "config.ini")
config = configparser.ConfigParser()
config.read(config_path)
url = config['backstage']['url']
username = config['backstage']['user']
user_password = config['backstage']['password']
agent = sys.argv[1]
token = config['token'][agent]
g_id = sys.argv[2].strip().upper()
date_time = sys.argv[3]
today = time.strftime("%Y-%m-%d")
# 日期格式錯誤換今天
if not is_valid_date(date_time):
    date_time = today
else:
    date_time = date_time
history_resource = get_resource(url, token, 'CARD', g_id, date_time)
if history_resource is False:
    print('resource error')
else:
    result = history_resource.find_all("div", {'class': 'pstm_number'})
    rows = list()
    for r in result:
        r = r.text.strip()
        # SN
        for SN in history_resource.select(
                "#history > div:nth-child({}) > div > div.table-responsive > table > "
                "tbody > tr:nth-child(6) > td:nth-child(2)".format(r)):
            SN = SN.text.strip()
        # player
        for player in history_resource.select(
                "#history > div:nth-child({}) > div > div.table-responsive > table > "
                "tbody > tr:nth-child(2) > td".format(r)):
            player = player.text.strip().split(')')[1].replace(' ', '')
        # room
        for room in history_resource.select(
                "#history > div:nth-child({}) > div > div.table-responsive > table > "
                "tbody > tr:nth-child(6) > td:nth-child(1)".format(r)):
            room = room.text.strip()
        # win
        for win in history_resource.select(
                "#history > div:nth-child({}) > div > div.table-responsive > table > "
                "tbody > tr:nth-child(10) > td".format(r)):
            win = float(
                win.text.replace('\n', '').replace('\xa0', '').replace(' ', '').replace('+', '').replace(',', ''))
            coin_in = abs(win)
            if win <= 0:
                coin_out = 0
            else:
                coin_out = 2 * win
        row = [r, player, SN, room, win, coin_in, coin_out]
        rows.append(row)
    columns = ['Item', 'Player', 'SN', 'room', 'win', 'coin in', 'coin out']

    df = pd.DataFrame(data=rows, columns=columns)
    if df.size == 0:
        print('{} {} No Data'.format(agent, g_id))
    else:
        print('{} {} Game History'.format(agent, g_id))
        print(df)
        # performance by room
        room_count = df['room'].value_counts()
        rooms = df['room'].unique()
        players = df['Player'].unique()
        # print(players)
        r_s = df.groupby(['room']).agg({'coin in': 'sum', 'coin out': 'sum'})
        room_group = df.groupby(['room'])
        r_row = list()
        for r in rooms:
            room_number = ('%.0f' % room_index.get(r))
            coin_in = float(r_s.loc[r, 'coin in'])
            coin_out = float(r_s.loc[r, 'coin out'])
            net = coin_in - coin_out
            if coin_in == 0:
                rtp = '0.00%'
            else:
                rr = round(coin_out / coin_in * 100, 2)
                rr = ('%.2f' % rr)
                rtp = '{}%'.format(rr)
            people = ('%.0f' % len(room_group.get_group(r).groupby(['Player']).SN.nunique()))
            Game = room_count[r]
            avg = round(coin_in / Game, 2)
            coin_in = ('%.2f' % coin_in)
            coin_out = ('%.2f' % coin_out)
            net = ('%.2f' % net)
            avg = ('%.2f' % avg)
            Game = ('%.0f' % room_count[r])
            r_row.append([room_number, coin_in, coin_out, net, rtp, avg, people, Game])
        r_column = ['room', 'coin in', 'coin out', 'Net Win', 'rtp', 'avg bet', 'people', 'Game']
        room_df = pd.DataFrame(data=r_row, columns=r_column)
        room_df['room'] = room_df['room'].astype(object)
        room_df['coin in'] = room_df['coin in'].astype(object)
        room_df['coin out'] = room_df['coin out'].astype(object)
        room_df['Net Win'] = room_df['Net Win'].astype(object)
        room_df['avg bet'] = room_df['avg bet'].astype(object)
        room_df['people'] = room_df['people'].astype(object)
        room_df['Game'] = room_df['Game'].astype(object)
        room_df.sort_values(by=['room'], inplace=True)
        print('Game History_Game')
        print(room_df)
        # <!----Sum by Player----
        # 計算各玩家出現次數(series)
        player_count = df['Player'].value_counts()
        # 玩家列表
        players = df['Player'].unique()
        p_s = df.groupby(['Player']).agg({'coin in': 'sum', 'coin out': 'sum'})
        p_column = ['Player', 'coin in', 'coin out', 'Net Win', 'rtp', 'avg bet', 'Game']
        p_row = list()
        for Player in players:
            Game = player_count[Player]
            coin_in = float(p_s.loc[Player, 'coin in'])
            coin_out = float(p_s.loc[Player, 'coin out'])
            NetWin = round(coin_in - coin_out, 2)
            if coin_in == 0:
                RTP = '0.00%'
            else:
                rr = round(coin_out / coin_in * 100, 2)
                rr = ('%.2f' % rr)
                RTP = '{}%'.format(rr)
            Avg = round(coin_in / Game, 2)
            coin_in = ('%.2f' % coin_in)
            coin_out = ('%.2f' % coin_out)
            NetWin = ('%.2f' % NetWin)
            Avg = ('%.2f' % Avg)
            Game = ('%.0f' % Game)
            p_row.append([Player, coin_in, coin_out, NetWin, RTP, Avg, Game])
        player_df = pd.DataFrame(data=p_row, columns=p_column)
        player_df['Player'] = player_df['Player'].astype(object)
        player_df['coin in'] = player_df['coin in'].astype(object)
        player_df['coin out'] = player_df['coin out'].astype(object)
        player_df['Net Win'] = player_df['Net Win'].astype(object)
        player_df['avg bet'] = player_df['avg bet'].astype(object)
        player_df['Game'] = player_df['Game'].astype(object)
        player_df.sort_values(by=['Player'], inplace=True)
        print('Game History_Player')
        print(player_df)

        login_status = login(url, username, user_password)
        if login_status != 'login successfully':
            print(login_status)
        else:
            performance_status = get_performance(url, date_time, agent, g_id, 'CARD')
            if isinstance(performance_status, str):
                print(performance_status)
            else:
                # print(performance_status)
                table = performance_status.find(id='DataTables_Table_3')
                tr = table.find_all('tr')
                rows = list()
                for r in range(1, len(tr) - 1):
                    for room in performance_status.select(
                            "#DataTables_Table_3 > tbody > tr:nth-child({}) > td:nth-child(4)".format(r)):
                        room = room.text.strip()
                        # print(room)
                    for coin_in in performance_status.select(
                            "#DataTables_Table_3 > tbody > tr:nth-child({}) > td:nth-child(5)".format(r)):
                        coin_in = coin_in.text.strip().replace(',', '')
                        # print(coin_in)
                    for coin_out in performance_status.select(
                            "#DataTables_Table_3 > tbody > tr:nth-child({}) > td:nth-child(6)".format(r)):
                        coin_out = coin_out.text.strip().replace(',', '')
                        # print(coin_out)
                    for net in performance_status.select(
                            "#DataTables_Table_3 > tbody > tr:nth-child({}) > td:nth-child(7)".format(r)):
                        net = net.text.strip().replace(',', '')
                        # print(net)
                    for rtp in performance_status.select(
                            "#DataTables_Table_3 > tbody > tr:nth-child({}) > td:nth-child(8)".format(r)):
                        rtp = rtp.text.strip().replace(',', '')
                        # print(rtp)
                    for avg in performance_status.select(
                            "#DataTables_Table_3 > tbody > tr:nth-child({}) > td:nth-child(9)".format(r)):
                        avg = avg.text.strip().replace(',', '')
                        # print(avg)
                    for people in performance_status.select(
                            "#DataTables_Table_3 > tbody > tr:nth-child({}) > td:nth-child(10)".format(r)):
                        people = people.text.strip().replace(',', '')
                        # print(people)
                    for games in performance_status.select(
                            "#DataTables_Table_3 > tbody > tr:nth-child({}) > td:nth-child(11)".format(r)):
                        games = games.text.strip().replace(',', '')
                        # print(games)
                    row = [room, coin_in, coin_out, net, rtp, avg, people, games]
                    rows.append(row)

                columns = ['room', 'coin in', 'coin out', 'Net Win', 'rtp', 'avg bet', 'people', 'Game']
                df_performance = pd.DataFrame(data=rows, columns=columns)
                is_zero = df_performance.iat[0, 7]
                if is_zero != '0':
                    print('Game Performance_Game')
                    print(df_performance)
                    player_performance = get_performance_player(url, date_time, agent, g_id)
                    if player_performance is False:
                        print(player_performance)
                    else:
                        # print(player_performance)
                        player_table = player_performance.find(id='DataTables_Table_4')
                        player_tr = player_table.find_all('tr')
                        player_rows = list()
                        for r in range(1, len(player_tr) - 1):
                            for player in player_performance.select(
                                    "#DataTables_Table_4 > tbody > tr:nth-child({}) > td:nth-child(1)".format(r)):
                                player = player.text.strip()
                                # print(player)
                            for player_coin_in in player_performance.select(
                                    "#DataTables_Table_4 > tbody > tr:nth-child({}) > td:nth-child(3)".format(r)):
                                player_coin_in = player_coin_in.text.strip().replace(',', '')
                                # print(player_coin_in)
                            for player_coin_out in player_performance.select(
                                    "#DataTables_Table_4 > tbody > tr:nth-child({}) > td:nth-child(4)".format(r)):
                                player_coin_out = player_coin_out.text.strip().replace(',', '')
                                # print(player_coin_out)
                            for player_net in player_performance.select(
                                    "#DataTables_Table_4 > tbody > tr:nth-child({}) > td:nth-child(10)".format(r)):
                                player_net = player_net.text.strip().replace(',', '')
                                # print(player_net)
                            for player_rtp in player_performance.select(
                                    "#DataTables_Table_4 > tbody > tr:nth-child({}) > td:nth-child(11)".format(r)):
                                player_rtp = player_rtp.text.strip().replace(',', '')
                                # print(player_rtp)
                            for player_avg in player_performance.select(
                                    "#DataTables_Table_4 > tbody > tr:nth-child({}) > td:nth-child(12)".format(r)):
                                player_avg = player_avg.text.strip().replace(',', '')
                                # print(player_avg)
                            for player_games in player_performance.select(
                                    "#DataTables_Table_4 > tbody > tr:nth-child({}) > td:nth-child(13)".format(r)):
                                player_games = player_games.text.strip().replace(',', '')
                                # print(player_games)
                            row = [player, player_coin_in, player_coin_out, player_net, player_rtp, player_avg,
                                   player_games]
                            player_rows.append(row)
                        player_columns = ['Player', 'coin in', 'coin out', 'Net Win', 'rtp', 'avg bet', 'Game']
                        player_p_df = pd.DataFrame(data=player_rows, columns=player_columns)
                        player_p_df.sort_values(by=['Player'], inplace=True)
                        print('Game Performance_Player')
                        print(player_p_df)
                        print('comparison by room')
                        result2 = room_df.merge(df_performance, how='outer', indicator=True).replace('both', 'PASS')
                        print(result2)
                        print('comparison by player')
                        result3 = player_df.merge(player_p_df, how='outer', indicator=True).replace('both', 'PASS')
                        print(result3)
                        filename = './{}_{}_{}.csv'.format(agent, g_id, date_time)
                        print('---製作報表 {}---'.format(filename))
                        info = pd.DataFrame({'Game ID': g_id, 'Agent': agent}, index=[1])
                        skip = pd.DataFrame()
                        history_list = pd.DataFrame({'history_sum': 'List of History'}, index=[1])
                        history_room = pd.DataFrame({'player_sum': 'Game History by room'}, index=[1])
                        history_player = pd.DataFrame({'history_sum': 'Game History by player'}, index=[1])
                        performance_room = pd.DataFrame({'player_sum': 'Game performance by room'}, index=[1])
                        performance_player = pd.DataFrame({'player_sum': 'Game performance by player'}, index=[1])
                        Comparison_result = pd.DataFrame({'Comparison_result': 'Comparison Result'}, index=[1])

                        info.to_csv(filename, encoding='utf-8', index=False)
                        skip.to_csv(filename, encoding='utf-8', index=False, mode='a')
                        history_list.to_csv(filename, encoding='utf-8', index=False, header=False, mode='a')
                        df.to_csv(filename, encoding='utf-8', index=False, mode='a')
                        skip.to_csv(filename, encoding='utf-8', index=False, mode='a')
                        history_room.to_csv(filename, encoding='utf-8', index=False, header=False, mode='a')
                        room_df.to_csv(filename, encoding='utf-8', index=False, mode='a')
                        skip.to_csv(filename, encoding='utf-8', index=False, mode='a')
                        history_player.to_csv(filename, encoding='utf-8', index=False, header=False, mode='a')
                        player_df.to_csv(filename, encoding='utf-8', index=False, mode='a')
                        skip.to_csv(filename, encoding='utf-8', index=False, mode='a')
                        performance_room.to_csv(filename, encoding='utf-8', index=False, header=False, mode='a')
                        df_performance.to_csv(filename, encoding='utf-8', index=False, mode='a')
                        skip.to_csv(filename, encoding='utf-8', index=False, mode='a')
                        performance_player.to_csv(filename, encoding='utf-8', index=False, header=False, mode='a')
                        player_p_df.to_csv(filename, encoding='utf-8', index=False, mode='a')
                        skip.to_csv(filename, encoding='utf-8', index=False, mode='a')
                        Comparison_result.to_csv(filename, encoding='utf-8', index=False, header=False, mode='a')
                        result2.to_csv(filename, encoding='utf-8', index=False, mode='a')
                        result3.to_csv(filename, encoding='utf-8', index=False, mode='a')
                else:
                    print('Performance no data')
        logout()
