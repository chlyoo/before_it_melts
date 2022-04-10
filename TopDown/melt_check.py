from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller
import json
import pymongo
from datetime import datetime


class MeltCheck():
    def __init__(self, dbu, debug):
        self.dbu = dbu
        self.db = self.dbu.get_db()
        self.collection = self.dbu.get_collection()
        self.debug = debug
        self.service = None
        self.option = None
        self.driver = None
        self.init_driver_option()
        self.notion_element = None
        self.menu_elements = None
        self.inter_result = None
        self.menu_data = self._parse_menu_data()
        self._insert_menu_to_db()

    def init_driver_option(self):
        self.service = Service(chromedriver_autoinstaller.install())
        self.option = webdriver.ChromeOptions()
        self.option.add_argument('headless')
        self.option.add_argument('--no-sandbox')
        self.option.add_argument('--disable-dev-shm-usage')

    def init_driver(self, debug=False):
        if self.debug:
            self.driver = webdriver.Chrome(service=self.service)
            return
        self.driver = webdriver.Chrome(service=self.service, options=self.option)

    def init_mongo_db(self):
        print("initialize mongo db for first install")
        self.collection.insert_one({"menu": self.menu_data, "date": datetime.now().strftime('%y%m%d')})

    def sync(self):
        self.menu_data = self._parse_menu_data()
        self._insert_menu_to_db()
        return self.menu_data

    def _parse_menu_data(self):
        try:
            self.init_driver()
            notion_element = self._get_notion_element()
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
        return inter_result[:-2]

    def _get_notion_element(self):
        url = 'https://beforeitmelts.notion.site/beforeitmelts/b261c537bf9a4fa79a94c3b8a79fa573'
        self.driver.get(url)
        self.driver.switch_to.parent_frame()
        self.driver.implicitly_wait(5)
        page_content = self.driver.find_element(By.CLASS_NAME, 'notion-page-content')
        return page_content

    @staticmethod
    def get_child_elements(parent, child_type: By, child_name: str):
        children = parent.find_elements(child_type, child_name)
        return children

    @staticmethod
    def get_text_of_list(source: webdriver.remote.webelement.WebElement):
        return list(map(lambda x: x.text, source))

    def _insert_menu_to_db(self):
        data = None
        try:
            data = json.dumps(self.menu_data)
            self.collection.insert_one({"menu": data, "date": datetime.now().strftime('%y%m%d')})
        except pymongo.errors.ServerSelectionTimeoutError:
            self.init_mongo_db()
            print("initialized")
            return
        except json.JSONDecodeError:
            data = json.dumps(self._parse_menu_data)
            self.collection.insert_one({"menu": data, "date": datetime.now().strftime('%y%m%d')})
        # print('synced')

    def _get_menu_from_db(self):
        data = self.collection.find_one({"date": datetime.now().strftime('%y%m%d')},
                                        sort=[('date', pymongo.DESCENDING)])
        data = data['menu']
        try:
            data = json.loads(data)
        except json.decoder.JSONDecodeError:
            print('Invalid Data')
            return None
        # print(data)
        return data

    def _get_instance_menu(self) -> list:
        return self.menu_data

    def _set_instance_menu(self, input_data):
        self.menu_data = input_data

    def request_data(self):
        self.menu = self._get_menu_from_db()
        if self.menu is None:
            self.menu = self.sync()
        return self.menu

if __name__ == '__main__':
    import config
    from models.db_components import MongoDB
    meltcheck_mongo = MongoDB(config.MONGODB_URL, 'meltcheck', 27017, config.MONGODB_ID, config.MONGODB_PW)
    meltcheck_mongo.set_collection('menu')
    mc = MeltCheck(meltcheck_mongo, config.DEBUG)
