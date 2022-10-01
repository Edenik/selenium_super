from pathlib import Path


class Auth:
    def __init__(self, driver):
        self.driver = driver

    def load_cookies(self, cookies):
        try:
            for cookie in cookies:
                self.add_cookie(cookie)
        except Exception as e:
            print('Error loading cookies, {}'.format(e))

    def load_auth_data(self, folder_path):
        has_auth_data = Path(folder_path + 'auth.json').is_file()

        if (has_auth_data):
            auth_file = self.driver.file_utils.load_json_file(folder_path + './auth.json')
            local_storage = auth_file.get('localstorage', [])

            try:
                for key, value in local_storage.items():
                    self.local_storage.set(key, value)
            except Exception as e:
                print('Error loading local storage items, {}'.format(e))

            self.load_cookies(auth_file.get('cookies', []))

        return has_auth_data

    def save_auth_data(self, folder_path):
        obj = {}
        local_storage_items = self.local_storage.items().items()

        for key, value in local_storage_items:
            obj[key] = value

        self.file_utils.write_json_file(folder_path + 'auth.json',
                                    "w+", {
                                        'cookies': self.driver.get_cookies(),
                                        'localstorage': obj
                                    },
                                    stringify=True)

    def do_login(self, login_url, username, password, elements, fetch_url=True):
        """
        Args:
            login_url (str): login url of the service
            username (str): username / email of the user
            password (str): user password
            elements (dict(dict("by", "value"))):
                        dict with 3 keys:
                        "user_input"
                        "pass_input"
                        "login_button:

                        each key should contain a dict
                        with the following keys: (example)
                        {
                            "user_input" : {"by": By.NAME, "value" : "username"},
                            "pass_input" : {"by": By.NAME, "value" : "Password"},
                            "login_button" : {"by": By.ID, "value" : "submitbut"}
                        }
            fetch_url (bool : optional): default set to true

        Returns:
            if success -
                True
            else:
                False
        """

        success = False
        validated_user_input = self.driver.validate_element(
            elements.get('user_input', {}))
        validate_pass_input = self.driver.validate_element(
            elements.get('pass_input', {}))
        validated_login_button = self.driver.validate_element(
            elements.get('login_button', {}))

        if validate_pass_input is False or validated_user_input is False or validated_login_button is False:
            print('properties are not valid')
            return False

        try:
            if fetch_url: self.driver.get(login_url)

            user_input = self.driver.find_element(
                by=elements['user_input']['by'], value=elements['user_input']['value'])
            user_input.send_keys(username)
            user_input.send_keys('\ue00c')
            pass_input = self.driver.find_element(
                by=elements['pass_input']['by'], value=elements['pass_input']['value'])
            pass_input.send_keys(password)
            pass_input.send_keys('\ue00c')
            button = self.driver.find_element(
                by=elements['login_button']['by'], value=elements['login_button']['value'])
            button.click()
            success = True

        except Exception as e:
            print('Error while trying login to -\n{}\n[Error] - {}'.format(
                login_url, e))

        return success

