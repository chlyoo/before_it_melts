from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller
import json
import pymongo
from datetime import datetime


class MeltCheck():
    def __init__(self, dbu, debug):
        self.driver = None
        self.debug = debug
        self.init_driver_option()
        self.init_driver(debug)
        self.notion_element = None
        self.menu_elements = None
        self.inter_result = None
        self.menu_data = self.parse_menu_data()
        self.dbu = dbu
        self.db = self.dbu.get_db()
        self.collection = self.dbu.get_collection()
        self.service = None
        self.option = None
        self.insert_menu_db()

    def init_driver_option(self, debug=False):
        self.service = Service(chromedriver_autoinstaller.install())
        if debug:
            self.driver = webdriver.Chrome(service=s)
            return
        self.option = webdriver.ChromeOptions()
        self.option.add_argument('headless')
        self.option.add_argument('--no-sandbox')
        self.option.add_argument('--disable-dev-shm-usage')

    def init_driver(self, debug=False):
        self.driver = webdriver.Chrome(service=self.service, options=self.option)

    def init_mongo_db(self):
        print("initialize mongo db for first install")
        self.collection.insert_one({"menu": self.menu_data, "date": datetime.now().strftime('%y%m%d %HH')})

    def sync(self):
        data = self.parse_menu_data()
        self.insert_menu_db()

    def parse_menu_data(self):
        try:
            self.init_driver()
            notion_element = self.get_notion_element()
            if self.notion_element == notion_element:
                if self.menu_data is not None:
                    return self.menu_data
            menu_elements = self.get_child_elements(notion_element, By.CLASS_NAME, 'notion-bulleted_list-block')
            if self.menu_elements == menu_elements:
                if self.menu_data is not None:
                    return self.menu_data
            inter_result = self.get_text_of_list(menu_elements)  # 배민 링크 제거
            if self.inter_result == inter_result:
                if self.menu_data is not None:
                    return self.menu_data
            self.driver.close()
        except Exception as e:
            print(e)
            return None
        self.menu_data = inter_result[:-1]
        return inter_result[:-1]

    def get_notion_element(self):
        url = 'https://beforeitmelts.notion.site/beforeitmelts/b261c537bf9a4fa79a94c3b8a79fa573'
        self.driver.get(url)
        self.driver.switch_to.parent_frame()
        self.driver.implicitly_wait(3)
        page_content = self.driver.find_element(By.CLASS_NAME, 'notion-page-content')
        return page_content

    @staticmethod
    def get_child_elements(parent, child_type: By, child_name: str):
        children = parent.find_elements(child_type, child_name)
        return children

    @staticmethod
    def get_text_of_list(source: webdriver.remote.webelement.WebElement):
        return list(map(lambda x: x.text, source))

    def insert_menu_db(self):
        data = json.dumps(self.menu_data)
        try:
            self.collection.insert_one({"menu": data, "date": datetime.now().strftime('%y%m%d %HH')})
        except pymongo.errors.ServerSelectionTimeoutError:
            self.init_mongo_db()
            print("initialized")
            return
        print('synced')

    def get_menu_from_db(self):
        data = self.collection.find_one({"date": datetime.now().strftime('%y%m%d %HH')},
                                        sort=[('date', pymongo.DESCENDING)])
        data = data['menu']
        try:
            data = json.loads(data)
        except json.decoder.JSONDecodeError:
            print('Invalid Data')
            return None
        return data

    def get_menu_data(self):
        db_data = self.get_menu_from_db()
        self.set_menu_data(db_data)
        return self.menu_data

    def set_menu_data(self, input_data):
        self.menu_data = input_data
