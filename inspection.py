from datetime import date
from driver_setting import driver_init
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import time


# 檢查日期格式
def is_valid_date(str_date):
    try:
        date.fromisoformat(str_date)
    except ValueError:
        return False
    else:
        return True


# 比對歷史紀錄與績效
def comparison(item, history, performance):
    if float(history) == float(performance):
        comparison_result = [item, history, performance, '[PASS]']
    else:
        comparison_result = [item, history, performance, '[FAIL]']
    return comparison_result


driver = driver_init()
wait = WebDriverWait(driver, 3)


def login(url, user, pwd):
    try:
        driver.get(url)
        try:
            print('---登入中---')
            wait_login = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="lang"]')))
            user_id = driver.find_element_by_id('user_id')
            password = driver.find_element_by_id('password')
            user_id.send_keys(user)
            password.send_keys(pwd)
            password.submit()
            try:
                wait_main = wait.until(EC.presence_of_element_located((
                    By.XPATH, '/html/body/div[3]/div/div[4]/div[1]/div/div/h4/span')))
                login_status = 'login successfully'
                return login_status
            except TimeoutException:
                login_status = 'login failed2'
                return login_status
        except TimeoutException:
            login_status = 'login failed1'
            return login_status
    except WebDriverException:
        login_status = 'page down'
        return login_status


# 擷取歷史紀錄
def get_history(url, date_time, agent_value, g_id, game_type):
    driver.get(url + '/Player/game_history')
    try:
        wait_history = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="sh_btn"]')))
        print('---遊戲紀錄擷取中---')
        # 輸入日期
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
        # 遊戲類型
        select_game_type = Select(driver.find_element_by_id('game_type'))
        if game_type == 'fish':
            game_type = 'PSF%'
        elif game_type == 'card':
            game_type = 'PSC%'
        else:
            game_type = 'PSS%'
        select_game_type.select_by_value(game_type)
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
            # 遊戲紀錄 html
            history_status = BeautifulSoup(driver.page_source, "html.parser")
            return history_status
        except TimeoutException:
            history_status = 'no data'
            return history_status
    except TimeoutException:
        history_status = 'enter history failed'
        return history_status


def get_performance(url, date_time, agent_value, g_id, game_type):
    driver.get(url + '/Accounting/game_performance')
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
            if game_type == 'slot':
                xpath = '//*[@id="DataTables_Table_1_filter"]/label/input'
                bet_p_path = '//*[@id="DataTables_Table_1"]/tbody/tr/td[4]'
                win_p_path = '//*[@id="DataTables_Table_1"]/tbody/tr/td[5]'
                bonus_p_path = '//*[@id="DataTables_Table_1"]/tbody/tr/td[6]'
                jp_p_path = '//*[@id="DataTables_Table_1"]/tbody/tr/td[8]'
                net_p_path = '//*[@id="DataTables_Table_1"]/tbody/tr/td[11]'
                rtp_p_path = '//*[@id="DataTables_Table_1"]/tbody/tr/td[12]'
                avg_p_path = '//*[@id="DataTables_Table_1"]/tbody/tr/td[13]'
                g_p_path = '//*[@id="DataTables_Table_1"]/tbody/tr/td[14]'
                people_p_path = '//*[@id="DataTables_Table_1"]/tbody/tr/td[15]'
            else:
                xpath = '//*[@id="DataTables_Table_1_filter"]/label/input'
                bet_p_path = '//*[@id="DataTables_Table_1"]/tbody/tr/td[4]'
                win_p_path = '//*[@id="DataTables_Table_1"]/tbody/tr/td[5]'
                bonus_p_path = '//*[@id="DataTables_Table_1"]/tbody/tr/td[6]'
                jp_p_path = '//*[@id="DataTables_Table_1"]/tbody/tr/td[8]'
                net_p_path = '//*[@id="DataTables_Table_1"]/tbody/tr/td[11]'
                rtp_p_path = '//*[@id="DataTables_Table_1"]/tbody/tr/td[12]'
                avg_p_path = '//*[@id="DataTables_Table_1"]/tbody/tr/td[13]'
                g_p_path = '//*[@id="DataTables_Table_1"]/tbody/tr/td[14]'
                people_p_path = '//*[@id="DataTables_Table_1"]/tbody/tr/td[15]'
            driver.find_element_by_xpath(xpath).send_keys(g_id)
            time.sleep(2)
            # 遊戲績效-遊戲-老虎機列表資料
            bet_p = driver.find_element_by_xpath(bet_p_path).text.strip().replace(',', '')
            win_p = driver.find_element_by_xpath(win_p_path).text.strip().replace(',', '')
            bonus_p = driver.find_element_by_xpath(bonus_p_path).text.strip().replace(',', '')
            jp_p = driver.find_element_by_xpath(jp_p_path).text.strip().replace(',', '')
            net_p = driver.find_element_by_xpath(net_p_path).text.strip().replace(',', '')
            rtp_p = driver.find_element_by_xpath(rtp_p_path).text.strip().replace(',', '')
            avg_p = driver.find_element_by_xpath(avg_p_path).text.strip().replace(',', '')
            g_p = driver.find_element_by_xpath(g_p_path).text.strip().replace(',', '')
            people_p = driver.find_element_by_xpath(people_p_path).text.strip().replace(',', '')
            performance_status = [bet_p, win_p, bonus_p, jp_p, net_p, rtp_p, avg_p, g_p, people_p]
            return performance_status
        except TimeoutException:
            print('load game_performance failed')
            performance_status = 'load game_performance failed'
            return performance_status
    except TimeoutException:
        print('enter game_performance failed')
        performance_status = 'enter game_performance failed'
        return performance_status


def logout():
    driver.quit()

