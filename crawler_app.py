import sys
from NEWS_Crawer.style import *
from time import strftime
from warnings import warn
from PyQt6 import QtWidgets as qtw
from PyQt6 import QtCore as qtc
from PyQt6 import QtGui as qtg
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel

from NEWS_Crawer.crawler import Crawler
from NEWS_Crawer.db import DB

import datetime

BASE_URL = "https://faktor.bg/bg/articles/novini"


class TableView(qtw.QTableView):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.db = DB()
        if not self.db.conn:
            qtw.QMessageBox.critical(
                None,
                "Database Error!",
                "Database Error: %s" % self.db.conn.lastError().databaseText(),
            )
        else:
            print('Succeed')

        self.data = self.db.select_all_data()
        self.column_names = self.db.get_column_names()
        model = self.setup_model()
        self.filter_proxy_model = qtc.QSortFilterProxyModel()
        self.filter_proxy_model.setSourceModel(model)
        self.filter_proxy_model.setFilterCaseSensitivity(qtc.Qt.CaseSensitivity.CaseInsensitive)
        self.filter_proxy_model.setFilterKeyColumn(1)
        self.setModel(self.filter_proxy_model)
        self.setup_gui()
        self.indexRow=1
        self.indexCol=1
        self.setMouseTracking(True)
        self.set_content_box()
        self.entered.connect(self.display_text)
        self.clicked.connect(self.dialog_freeze)
    def set_content_box(self):
        self.dialog = qtw.QDialog(parent=self)
        self.dialog.setAttribute(qtc.Qt.WidgetAttribute.WA_QuitOnClose)
        self.dialog.setAttribute(qtc.Qt.WidgetAttribute.WA_StyledBackground)
        self.dialog.setAutoFillBackground(True)
        self.dialog.setWindowTitle("Current news detail")
        self.dialog.setWindowIcon(qtg.QIcon("./NEWS_Crawer/icons/book.png"))
        self.dialog.setStyleSheet(QSS)
        self.dialog.move(483,254)
        # Create a label with a message
        label = qtw.QLabel("This is a message in the dialog box.")
        label.setObjectName("message")
        # Create a layout for the dialog
        scroll_area=qtw.QScrollArea()
        scroll_area.setObjectName("scroll_area")
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(label)

        dialog_layout = qtw.QVBoxLayout()
        # dialog_layout.addWidget(label)
        dialog_layout.addWidget(scroll_area)
      # Set the layout for the dialog
        self.dialog.setGeometry(500,200,500,200)
        self.dialog.setLayout(dialog_layout)

        # self.dialog.show()
    def display_text(self,index):
        if index.row()>=0 and index.column()==3:
            if index.row!=self.indexRow or index.column!=self.indexCol:
                if self.dialog.isVisible():
                    self.dialog.hide()
                self.indexRow=index.row()
                self.indexCol=index.column()
                self.dialog.move(298,self.rowViewportPosition(index.row())+60)
                new_label = qtw.QLabel(index.data(qtc.Qt.ItemDataRole.UserRole))
                new_label.setWordWrap(True)
                new_label.setMaximumHeight(200)
                new_label.setMinimumWidth(300)
                new_label.setContentsMargins(20,20,20,20)
                scroll=self.dialog.findChild(qtw.QScrollArea,"scroll_area")
                scroll.setWidget(new_label)
                self.dialog.show()
        else:
            if self.dialog.isVisible():
                self.dialog.hide()
    def dialog_freeze(self):
        if self.dialog.isVisible():
            self.dialog.close()
            self.dialog.move(700,self.rowViewportPosition(self.indexRow)+60)
            self.dialog.exec()
        else:pass
    def setup_model(self):
        model = qtg.QStandardItemModel()
        print(self.column_names)
        model.setHorizontalHeaderLabels(self.column_names)

        for i, row in enumerate(self.data):
            items = []
            for field in row:
                item = qtg.QStandardItem()
                if isinstance(field, datetime.date):
                    field = field.strftime('%d.%m.%Y')
                    pass
                elif isinstance(field, str) and len(field) > 100:
                    # set full string with UserRole for later use:
                    item.setData(field, qtc.Qt.ItemDataRole.UserRole)
                    # trim string for display
                    field = field[0:50] + '...'
                item.setData(field, qtc.Qt.ItemDataRole.DisplayRole)
                items.append(item)
            model.insertRow(i, items)
        return model

    def setup_gui(self):
        ### set table dimensions:
        # get rows and columns count from model:
        rows_count = self.model().rowCount()
        cols_count = self.model().columnCount()
        # self.setVerticalScrollBarPolicy(qtc.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setMinimumWidth(cols_count * 230)
        # self.setMinimumHeight(rows_count * 40)
        self.setMinimumHeight(800)

        ### resize cells to fit the content:
        # self.resizeRowsToContents()
        # self.resizeColumnsToContents()
        # set width of separate columns:
        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)
        self.setColumnWidth(3, 300)

        # streach table:
        # self.horizontalHeader().setSectionResizeMode(qtw.QHeaderView.Stretch)
        # self.horizontalHeader().setStretchLastSection(True)
        # self.verticalHeader().setSectionResizeMode(qtw.QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(qtw.QHeaderView.ResizeMode.ResizeToContents)

        # set all cells height
        # header = self.verticalHeader()
        # header.setDefaultSectionSize(50)
        # header.setSectionResizeMode(qtw.QHeaderView.Fixed)

        # enable columns move
        # self.horizontalHeader().setSectionsMovable(True)

        # enable columns sort
        self.setSortingEnabled(True)
        self.sortByColumn(0, qtc.Qt.SortOrder.AscendingOrder)


    @qtc.pyqtSlot(int)
    def set_filter_column(self, index):
        self.filter_proxy_model.setFilterKeyColumn(index)

    def get_last_updated_date(self):
        last_updated_date = self.db.get_last_updated_date()
        return last_updated_date.strftime('%d.%m.%y, %H:%M:%S')


class TableViewWidget(qtw.QWidget):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.parent = parent

        self.setup_gui()

    def setup_gui(self):
        # table view:
        self.tableView = TableView()
        tableViewWidth = self.tableView.frameGeometry().width()
        tableViewHeight = self.tableView.frameGeometry().height()

        # label
        lblTitle = qtw.QLabel()
        label_msg = f'News publications as crawled on {self.tableView.get_last_updated_date()}'
        lblTitle.setText(label_msg)
        lblTitle.setStyleSheet('''
            font-size: 30px;
            margin:20px auto;
            color: purple;
        ''')
        lblTitle.setAlignment(qtc.Qt.AlignmentFlag.AlignCenter)

        # filter box layout:
        filterLabel = qtw.QLabel('Filter by column: ')
        filterLabel.setStyleSheet(QSS)

        filterLineEdit = qtw.QLineEdit()
        filterLineEdit.textChanged.connect(self.tableView.filter_proxy_model.setFilterRegularExpression)
        filterLineEdit.setStyleSheet(QSS)

        comboBox = qtw.QComboBox()
        comboBox.setStyleSheet(QSS)
        comboBox.addItems(["{0}".format(col) for col in self.tableView.column_names])
        comboBox.setCurrentText('title')
        comboBox.currentIndexChanged.connect(lambda idx: self.tableView.set_filter_column(idx))

        filterBoxLayout = qtw.QHBoxLayout()
        filterBoxLayout.addWidget(filterLabel)
        filterBoxLayout.addWidget(comboBox)
        filterBoxLayout.addWidget(filterLineEdit)

        # close button
        btnClose = qtw.QPushButton('Close')
        # btnClose.clicked.connect(self.close_all)
        # or with lambda syntax
        btnClose.clicked.connect(lambda _: self.close() and self.parent.close())

        # main layout
        layout = qtw.QVBoxLayout()
        layout.addWidget(lblTitle)
        layout.addLayout(filterBoxLayout)
        layout.addWidget(self.tableView)
        layout.addWidget(btnClose)

        self.setLayout(layout)

        self.setFixedWidth(tableViewWidth)
        # self.setFixedHeight(tableViewHeight)

    def close_all(self):
        self.parent.close()
        self.close()
    #
    @qtc.pyqtSlot(int)
    def on_comboBox_currentIndexChanged(self, index):
        self.tableView.filter_proxy_model.setFilterKeyColumn(index)



    def get_current_datetime(self):
        return datetime.datetime.now().strftime('%d.%m.%y, %H:%M:%S')


class MainWindow(qtw.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.crawler = Crawler(BASE_URL)

        self.setWindowTitle('NEWS Crawler')
        self.setWindowIcon(qtg.QIcon("./NEWS_Crawer/icons/book.png"))
        self.setGeometry(300,300,300,300)

        ### Main layout
        mainLayout = qtw.QVBoxLayout()

        ### Table Caption part:
        lblTableCaption = qtw.QLabel('NEWS DATA')
        lblTableCaption.setObjectName('lblTableCaption')
        lblTableCaption.setAlignment(qtc.Qt.AlignmentFlag.AlignCenter)
        mainLayout.addWidget(lblTableCaption)

        ### Buttons
        btnsLayout = qtw.QHBoxLayout()
        btnCrawlerRun = qtw.QPushButton('Run Crawler')
        self.btnShowData = qtw.QPushButton('Show Data')
        # self.btnShowData.setEnabled(False)

        btnsLayout.addWidget(btnCrawlerRun)
        btnsLayout.addWidget(self.btnShowData)
        mainLayout.addLayout(btnsLayout)

        ### Status
        ## will be hiddin on start
        statusLayout = qtw.QVBoxLayout()
        self.lblStatus = qtw.QLabel('Crawler Working...')
        self.lblStatus.hide()
        statusLayout.addWidget(self.lblStatus)
        mainLayout.addLayout(statusLayout)

        ### Actions on buttons click:
        self.btnShowData.clicked.connect(self.show_data)
        btnCrawlerRun.clicked.connect(self.run_crawler)

        # add spacer or just fixed spacing
        mainLayout.addSpacing(10)
        # mainLayout.addSpacerItem(qtw.QSpacerItem(0, 0, qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Expanding))

        mainWidget = qtw.QWidget()
        mainWidget.setLayout(mainLayout)

        self.setCentralWidget(mainWidget)

        self.show()
    def show_data(self):
        self.tableViewWidget = TableViewWidget(parent=self)
        self.tableViewWidget.show()

    def run_crawler(self):
        print('Crawler started')

        # change cursor to wait icon:
        self.setCursor(qtc.Qt.CursorShape.WaitCursor)

        # show status label
        self.lblStatus.show()
        qtw.QApplication.processEvents()  # needed to force processEvents

        # start crawler
        self.crawler.run()

        # if crawler ready:
        if self.crawler.status:
            self.lblStatus.setText('Ready!')
            self.btnShowData.setEnabled(True)

        self.setCursor(qtc.Qt.CursorShape.ArrowCursor)


if __name__ == '__main__':
    warn('Warning !', DeprecationWarning)
    app = qtw.QApplication(sys.argv)

    window = MainWindow()
    window.setStyleSheet(QSS)

    sys.exit(app.exec())
