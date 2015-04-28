from model.player import Player
from gui.login_manager import LoginManager
from gui.main_window import MainWindow


class Launcher:
    def login(self):
        account, autoconnect = LoginManager().do_login()
        if account:
            player = Player(account['uid'], account['auth'])
            main_window = MainWindow(player, account['name'], autoconnect)
            main_window.show()


if __name__ == '__main__':
    Launcher().login()
