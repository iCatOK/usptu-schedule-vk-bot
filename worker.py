from time import sleep
from selenium import webdriver
from selenium.webdriver import ActionChains
import os
import pandas as pd
from threading import Thread

LOGIN = 'enter login here'
PASSWORD = 'enter pass here'

def init_csv():
    if not os.path.exists('data.csv'):
        return None
    d = pd.read_csv('data.csv')
    d_new = d[['Название', 'Ссылка']]
    return d_new

def init_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    print('added options')
    return chrome_options


def login():
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=init_driver())
    # driver = webdriver.Chrome(options=init_driver())
    driver.get("https://ams.rusoil.net/pcs/aut")
    driver.find_element_by_link_text('Войти').click()

    print('entered to login page')

    driver.find_element_by_class_name('webix_inp_static').click()
    driver.find_element_by_xpath("//*[contains(text(), 'Сотовый (в формате 79270123456)')]").click()

    driver.find_element_by_xpath("//input[@type='text']").send_keys(LOGIN)
    driver.find_element_by_xpath("//input[@type='password']").send_keys(PASSWORD)

    action = ActionChains(driver)

    slider = driver.find_element_by_class_name("slide-to-unlock-handle")
    action.drag_and_drop_by_offset(slider, 255, 0).perform()

    print('slider check confirmed')
    driver.find_element_by_xpath("//*[contains(text(), 'Войти')]").click()

    sleep(3)

    driver.get('https://ams.rusoil.net/pcs/s?w_Rasp')
    print('entered to schedule')
    sleep(0.2)
    return driver

def get_schedule():
    driver = login()
    sleep(1)
    table_div = driver.find_element_by_id("Rasp")

    table_div.find_elements_by_tag_name('tr')[1].find_element_by_tag_name('a').click()
    print('open all schedule')
    sleep(0.2)
    return driver

def make_csv():
    driver = get_schedule()
    table_div = driver.find_element_by_id("Rasp")
    trs = table_div.find_elements_by_tag_name('tr')[2:]

    link_info = {
        'Название': [],
        'Ссылка': []
    }

    for i, tr in enumerate(trs):
        td = tr.find_elements_by_tag_name('td')[-1]
        links = td.find_elements_by_tag_name('a')
        if len(links) > 0:
            # print(td.text[0:-9])
            # print(links[0].get_attribute('href'))
            link_info['Название'].append(td.text[0:-9])
            link_info['Ссылка'].append(links[0].get_attribute('href'))
            os.environ['LAST_TR_INDEX'] = f'{2+i}'
            # print(os.environ.get('LAST_TR_INDEX'))
    links_df = pd.DataFrame.from_dict(link_info)
    last_link = [links_df.iloc[-1]['Название'], links_df.iloc[-1]['Ссылка']]
    links_df.to_csv("data.csv", encoding='utf-8-sig')
    
    print('made csv')
    driver.quit()
    return last_link

def debug_delete_last():
    links_df = init_csv()
    links_df.drop([len(links_df)-1], inplace=True)
    links_df.to_csv('data.csv')


def check_update():
    links_df = init_csv()
    if links_df is None:
        return make_csv()
    last_link = [links_df.iloc[-1]['Название'], links_df.iloc[-1]['Ссылка']]
    print(f'Последняя - {last_link}')

    driver = get_schedule()
    table_div = driver.find_element_by_id("Rasp")
    trs = table_div.find_elements_by_tag_name('tr')[2:]

    for i in range(int(os.environ.get('LAST_TR_INDEX'))+1, len(trs)):
        td = trs[i].find_elements_by_tag_name('td')[-1]
        links = td.find_elements_by_tag_name('a')

        if len(links) > 0:
            links_df.loc[len(links_df)] = [td.text[0:-9], links[0].get_attribute('href')]
            last_link = [td.text[0:-9]]
            last_link.append(links[0].get_attribute('href'))
            os.environ['LAST_TR_INDEX'] = f'{i}'
        else:
            break

    links_df.to_csv('data.csv')
    print('updated csv')
    print('last index - {}'.format(os.environ.get('LAST_TR_INDEX')))
    driver.quit()
    return last_link

def time_check_update():
    print('работа в потоке начата')
    last_link = check_update()
    print('Обновлена таблица data csv по времени')
    print('работа в потоке завершена')
    print('Последняя ссылка:  {}'.format(last_link))

def paralel_time_check_update():
    t = Thread(
        target=time_check_update, 
    )
    t.start()
