from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller
import pymongo
import json
from datetime import datetime
import time
import schedule
import secrets

def init_driver(test=True):
    s = Service(chromedriver_autoinstaller.install())
    if test:
        driver = webdriver.Chrome(service=s)
        return driver
    o = webdriver.ChromeOptions()
    o.add_argument('headless')
    o.add_argument('--no-sandbox')
    o.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=s, options=o)
    return driver

def get_notion_element(driver):
    url = 'https://beforeitmelts.notion.site/beforeitmelts/b261c537bf9a4fa79a94c3b8a79fa573'
    driver.get(url)
    driver.switch_to.parent_frame()
    driver.implicitly_wait(3)
    page_content = driver.find_element(By.CLASS_NAME, 'notion-page-content')
    return page_content

def get_child_elements(parent, child_type: By, child_name: str):
    children = parent.find_elements(child_type, child_name)
    return children

def get_text_of_list(source: webdriver.remote.webelement.WebElement):
    return list(map(lambda x : x.text, source))

def get_menus():
    client = _get_mongoclient()
    db = _get_mongo_db(client)
    return get_menu_from_db(db)
    # return main(False)

def get_menu_from_db(collection):
    if collection is None:
        collection = _get_mongo_db(_get_mongoclient())
    data = collection.find_one({"date": datetime.now().strftime('%y%m%d %HH')}, sort=[('date', pymongo.DESCENDING)])
    print(data)
    data = data['menu']
    print(data)
    try:
        data = json.loads(data)
    except json.decoder.JSONDecodeError:
        print('Invalid Data')
        return None
    return data

def insert_menu_db(collection):
    if collection is None:
        collection = _get_mongo_db(_get_mongoclient())
    data = parse_menu_data(False)
    data = json.dumps(data)
    try:
        db.insert_one({"menu": data, "date": datetime.now().strftime('%y%m%d %HH')})
    except pymongo.errors.ServerSelectionTimeoutError:
        init_mongo_db()
        print("initialized")
        return
    print('synced')

def _get_mongoclient():
    # client = pymongo.MongoClient("localhost", 27017)
    client = pymongo.MongoClient(f'mongodb://{secrets.MONGODB_ID}:{secrets.MONGODB_PW}@{secrets.MONGODB_URL}:27017/meltcheck')
    return client

def _get_mongo_db(client):
    return client.meltcheck['menu']

def init_mongo_db():
    print("initialize mongo db for install")
    client = _get_mongoclient()
    db = client['meltcheck']
    collection = db['menu']
    data = parse_menu_data(False)
    collection.insert_one({"menu": data, "date": datetime.now().strftime('%y%m%d %HH')})

def parse_menu_data(test=True):
    try:
        driver = init_driver(test)
        notion_element = get_notion_element(driver)
        menu_elements = get_child_elements(notion_element, By.CLASS_NAME, 'notion-bulleted_list-block')
        result = get_text_of_list(menu_elements) # 배민 링크 제거
        driver.close()
    except Exception as e:
        print(e)
        return None
    return result[:-1]

if __name__ == '__main__':
    client = _get_mongoclient()
    db = _get_mongo_db(client)
    insert_menu_db(db)
    schedule.every(3).minutes.do(insert_menu_db, db)  # 3분마다 job 실행
    while True:
        schedule.run_pending()
        time.sleep(1)