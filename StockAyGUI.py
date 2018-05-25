import sys
import time
import os, glob
import pandas as pd
import matplotlib.dates as mdates
from mpl_finance import candlestick_ohlc
import datetime

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout, \
    QFormLayout, QProgressBar
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, \
    QPushButton
from PyQt5.QtGui import QIcon

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import random


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.left = 10
        self.top = 10
        self.title = 'TS Stock Analysis GUI'
        self.width = 960
        self.height = 540
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # m = PlotCanvas(self, width=5, height=4)
        self.candlelit = PlotCandlit(self, width=5, height=4)

        # m.move(0, 0)

        self.line_hello = QLineEdit(self)
        self.line_hello.setText("2454")
        self.button_search = QPushButton('Search', self)
        self.button_search.setToolTip('Search and show the candlelit plot')
        # self.button_search.move(500, 0)

        form_layout = QFormLayout()
        form_layout.addRow(self.button_search, self.line_hello)
        # form_layout.addRow(self.line_hello)
        form_layout.addRow(self.candlelit)

        h_layout = QVBoxLayout()
        h_layout.addLayout(form_layout)

        self.setLayout(h_layout)

        # button.resize(140, 100)

        self.show()


# class PlotCanvas(FigureCanvas):
#     def __init__(self, parent=None, width=5, height=4, dpi=100):
#         fig = Figure(figsize=(width, height), dpi=dpi)
#         self.axes = fig.add_subplot(111)
#
#         FigureCanvas.__init__(self, fig)
#         self.setParent(parent)
#
#         FigureCanvas.setSizePolicy(self,
#                                    QSizePolicy.Expanding,
#                                    QSizePolicy.Expanding)
#         FigureCanvas.updateGeometry(self)
#         self.plot()
#
#     def plot(self):
#         data = [random.random() for i in range(25)]
#         ax = self.figure.add_subplot(211)
#         ax.plot(data, 'r-')
#         ax.set_title('PyQt Matplotlib Example')
#         ax2 = self.figure.add_subplot(212)
#         ax2.plot(data, 'r-')
#         ax2.set_title('PyQt Matplotlib Example')
#         self.draw()


class PlotCandlit(FigureCanvas):
    def __init__(self, parent=None, width=7, height=6, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        # self.axes2 = fig.add_subplot(212)


        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


        self.canvas = FigureCanvas(fig)

        #fig = plt.figure(figsize=(10, 60), facecolor='green', edgecolor='red')

        MAs = [5, 10, 20]  # Moving average of 5, 10, 20 days
        dfs1 = self.getDataByStockIdx(stockIdx=2454, MAs=MAs, days=60)
        self.candleStickPlot(dfs1=dfs1, MAs=MAs)



    def candleStickPlot(self, dfs1, MAs):
        df_candleStickPlot = dfs1[['Date', 'Open', 'Day_High', 'Day_Low', 'Close', 'Num_Deals']]
        df_candleStickPlot['Date'] = df_candleStickPlot['Date'].apply(mdates.date2num)

        # self.f1 = plt.subplot2grid((6, 4), (0, 0), rowspan=5, colspan=4, axisbg='#07000d')
        # f1 = self.axes.subplot2grid((6, 4), (0, 0), rowspan=5, colspan=4, axisbg='#07000d')
        f1 = self.figure.add_subplot(211)
        # plot candlestick
        candlestick_ohlc(f1, df_candleStickPlot.values, width=.6, colorup='#ff1717', colordown='#53c156')
        # ohlc = [] # should be something like [(1, 2, 3, 4, 5), (1, 2, 3, 4, 5), (1, 2, 3, 4, 5)] where 1, 2, 3, 4 refer to the date, open, high, low, close, volumn

        # plot MA
        for MA_value in MAs:
            ma_key = 'MA' + str(MA_value)
            f1.plot(dfs1['Date'], dfs1[ma_key])  # plot MA

        f1.set_title('2454')
        f1.axes.get_xaxis().set_visible(False)
        f1.set_ylabel('Price')

        # plot volumn
        # self.f2 = plt.subplot2grid((6, 4), (5, 0), rowspan=6, colspan=4, axisbg='#07000d')
        f2 = self.figure.add_subplot(212)
        f2.bar(dfs1['Date'], dfs1['Num_Deals'])
        f2.set_ylabel('Volume')

        plt.xticks(rotation=45)

        self.draw()
        # self.show()

    def getDataByStockIdx(self, stockIdx, MAs, days=30):
        keys = ['Date', 'Days_Trade', 'Turnover_Value', 'Open', 'Day_High', 'Day_Low', 'Close', 'Price_Dif',
                'Num_Deals']
        current_path = os.path.dirname(os.path.abspath(__file__)) + '/'
        data_folder = current_path + "data/"
        csv_file = data_folder + str(stockIdx) + '.csv'
        df = pd.read_csv(csv_file, names=keys)

        MA_max = max(MAs)

        df = df.tail(int(days) + int(MA_max) - 1)

        # preprocessing
        for idx in range(len(df)):
            ori_date_format = df['Date'].values[idx]
            new_date_format = ori_date_format.replace(ori_date_format[0:3], str(int(ori_date_format[0:3]) + 1911))
            new_date_format = datetime.datetime.strptime(new_date_format, '%Y/%m/%d').strftime('%Y-%m-%d')
            df['Date'].values[idx] = new_date_format

        df.Date = pd.to_datetime(df.Date)
        df.Open = df.Open.astype(float)
        df.Day_High = df.Day_High.astype(float)
        df.Day_Low = df.Day_Low.astype(float)
        df.Close = df.Close.astype(float)
        df.Num_Deals = df.Num_Deals.astype(float)

        # df_candleStickPlot = df_candleStickPlot.iloc[::-1] #revert the data

        # generate MA values
        for MA_value in MAs:
            new_key = 'MA' + str(MA_value)
            df[new_key] = df['Close'].rolling(int(MA_value)).mean()

        return df.tail(days)


class TutorialThread(QThread):
    set_max = pyqtSignal(int)
    update = pyqtSignal(int)

    def __init__(self):
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
        self.update.emit(100)
        for index in range(1, 101):
            self.update.emit(index)
            time.sleep(0.5)

class MainWindow(QWidget):
    def __init__(self):
        super(self.__class__, self).__init__()

        self.setupUi()
        self._tutorial_thread = TutorialThread()
        self._tutorial_thread.set_max.connect(self.set_max)
        self._tutorial_thread.update.connect(self.set_value)

        self.show()

    def setupUi(self):
        self.setWindowTitle("執行緒的使用")

        self.button_start = QPushButton()
        self.button_start.setText("開始")
        self.button_stop = QPushButton()
        self.button_stop.setText("結束")

        self.progress_bar = QProgressBar()

        self.line = QLineEdit()

        form_layout = QFormLayout()
        form_layout.addRow(self.button_start, self.line)
        form_layout.addRow(self.button_stop)
        form_layout.addRow(self.progress_bar)

        h_layout = QVBoxLayout()
        h_layout.addLayout(form_layout)

        self.setLayout(h_layout)

        self.button_start.clicked.connect(self.start)
        self.button_stop.clicked.connect(self.stop)

    def start(self):
        self.line.setText("觸發後可以修改")
        self._tutorial_thread.start()

    def stop(self):
        self._tutorial_thread.terminate()

    def set_max(self, data):
        self.progress_bar.setMaximum(data)

    def set_value(self, data):
        self.progress_bar.setValue(data)


if __name__ == "__main__":

    app = QApplication(sys.argv)

    # MainWindow = MainWindow()
    ex = App()
    ex.show()

    sys.exit(app.exec_())
