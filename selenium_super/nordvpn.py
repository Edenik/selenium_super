from nordvpn_switcher import initialize_VPN, rotate_VPN, terminate_VPN


class NordVPN:
    def __init__(self, countries=None):
        self.settings = None
        self.is_vpn_on = False

        if countries:
            self.set_countries(countries)

    def set_countries(self, countries):
        try:
            self.settings = initialize_VPN(area_input=countries)
        except Exception as e:
            print(e)

    def rotate(self, google_check=True):
        self.is_vpn_on = True
        if self.settings is not None:
            rotate_VPN(self.settings, google_check=1 if google_check else 0)
        else:
            print('Could not start vpn. Please use set_countries method before.')

    def terminate(self):
        self.settings = None
        self.is_vpn_on = False
        terminate_VPN()

