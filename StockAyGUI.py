import sys
from PyQt5.QtWidgets import QApplication, QWidget

class MainWindow(QWidget):

    def __init__(self):

        super(self.__class__, self).__init__()

        self.setupUi()

        self.show()



    def setupUi(self):

        self.setWindowTitle("Hello World!")





if __name__ == "__main__":

    app = QApplication(sys.argv)

    MainWindow = MainWindow()

    sys.exit(app.exec_())
