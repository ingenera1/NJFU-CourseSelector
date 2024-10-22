import sys
import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout,
                             QPushButton, QStackedWidget, QTextBrowser, QTableWidgetItem)
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5 import uic
from fcore import *


class FecthThread(QThread):
    data_fetched = pyqtSignal(list)

    def __init__(self, s: dict):
        super().__init__()
        self.settings = s

    def run(self):
        # 启动定时
        try:
            target_time_str = self.settings['Time']
            target_time = datetime.datetime.strptime(target_time_str, "%H:%M").time()
            while True:
                current_time = datetime.datetime.now().time()
                if current_time >= target_time:
                    break
                print('等待中..')
                time.sleep(0.5)

            # 获取公选课
            if self.settings['Type']:
                course_lis = get_public_course(cookie=self.settings['Cookie'], timeout=self.settings['Timeout'])
                if course_lis is None:
                    return
                # 有预先指定的课程的情况
                if self.settings['Expected'] != '':
                    kchs = self.settings['Expected'].split('+')
                    for kch in kchs:
                        for course in course_lis:
                            if kch == course['kch']:
                                return_msg = select_course(cookie=self.settings['Cookie'],
                                                           id02=course['02id'],
                                                           id04=course['04id'],
                                                           name=course['Name'],
                                                           is_public=True,
                                                           timeout=self.settings['Timeout']
                                                           )
                                print(return_msg)
                                break
                self.data_fetched.emit(course_lis)  # 发送数据

            # 获取体育课
            else:
                course_lis = get_pe_course(cookie=self.settings['Cookie'], class_num=self.settings['ClassNum'], timeout=self.settings['Timeout'])
                if course_lis is None:
                    return
                self.data_fetched.emit(course_lis)  # 发送数据

        except ValueError:
            print("目标时间格式（HH:MM）错误,或cookie无效") 


class FecthThread2(QThread):
    data_fetched = pyqtSignal(list)

    def __init__(self, s: dict):
        super().__init__()
        self.settings = s

    def run(self):
        # 获取公选课
        if self.settings['Type']:
            course_lis = get_public_course(cookie=self.settings['Cookie'], timeout=self.settings['Timeout'])
            if course_lis is None:
                return
            self.data_fetched.emit(course_lis)  # 发送数据

        # 获取体育课
        else:
            course_lis = get_pe_course(cookie=self.settings['Cookie'], class_num=self.settings['ClassNum'], timeout=self.settings['Timeout'])
            if course_lis is None:
                return
            self.data_fetched.emit(course_lis)  # 发送数据


class SelectThread(QThread):
    def __init__(self, d: dict, s: dict):
        super().__init__()
        self.data = d
        self.settings = s

    def run(self):
        return_msg = select_course(cookie=self.settings['Cookie'],
                                   id02=self.data['02id'],
                                   id04=self.data['04id'],
                                   name=self.data['Name'],
                                   is_public=self.settings['Type'],
                                   timeout=self.settings['Timeout']
                                   )
        print(return_msg)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setFixedSize(1080, 680)
        self.setWindowTitle('NJFU CourseSelector')
        self.course_type = self.ui1.radioButton.isChecked()
        self.class_num = self.ui1.lineEdit.text()
        self.spc_time = self.ui1.lineEdit_2.text()
        self.spc_courses = self.ui1.lineEdit_3.text()
        self.cookie = self.ui1.lineEdit_4.text()
        # self.fetch_interval = float(self.ui1.lineEdit_5.text())
        self.fetch_timeout = float(self.ui1.lineEdit_6.text())

        self.fetched_data = []  # 存储获取到的课程信息

    def init_ui(self):
        self.stacked_widget = QStackedWidget(self)

        # UI 1
        self.ui1 = uic.loadUi('../uis/1.ui')
        self.stacked_widget.addWidget(self.ui1)
        self.switch_btn_1t2 = self.ui1.findChild(QPushButton, "pushButton_3")
        self.switch_btn_1t2.clicked.connect(self.show_ui2)
        self.switch_btn_1t3 = self.ui1.findChild(QPushButton, "pushButton_4")
        self.switch_btn_1t3.clicked.connect(self.show_ui3)

        self.text_browser = self.ui1.textBrowser

        self.save_btn = self.ui1.pushButton
        self.save_btn.clicked.connect(self.save)

        # UI 2
        self.ui2 = uic.loadUi('../uis/2.ui')
        self.stacked_widget.addWidget(self.ui2)
        self.text_browser_2 = self.ui1.findChild(QTextBrowser, "textBrowser")

        self.switch_btn_2t1 = self.ui2.findChild(QPushButton, "pushButton_2")
        self.switch_btn_2t1.clicked.connect(self.show_ui1)
        self.switch_btn_2t3 = self.ui2.findChild(QPushButton, "pushButton_4")
        self.switch_btn_2t3.clicked.connect(self.show_ui3)

        self.launch_btn = self.ui2.launchButton
        self.launch_btn.clicked.connect(self.launch)
        self.confirm_btn = self.ui2.confirmButton
        self.confirm_btn.clicked.connect(self.confirm)
        self.refresh_btn = self.ui2.refreshButton
        self.refresh_btn.clicked.connect(self.refresh)
        self.table_widget = self.ui2.tableWidget

        # UI 3
        self.ui3 = uic.loadUi('../uis/3.ui')
        self.stacked_widget.addWidget(self.ui3)
        # self.text_browser = self.ui1.findChild(QTextBrowser, "textBrowser")

        self.switch_btn_3t1 = self.ui3.findChild(QPushButton, "pushButton_2")
        self.switch_btn_3t1.clicked.connect(self.show_ui1)
        self.switch_btn_3t2 = self.ui3.findChild(QPushButton, "pushButton_3")
        self.switch_btn_3t2.clicked.connect(self.show_ui2)

        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)

        self.stacked_widget.setCurrentWidget(self.ui1)  # 初始界面为 UI 1

    def show_ui1(self):
        self.stacked_widget.setCurrentWidget(self.ui1)

    def show_ui2(self):
        self.stacked_widget.setCurrentWidget(self.ui2)

    def show_ui3(self):
        self.stacked_widget.setCurrentWidget(self.ui3)

    def save(self):
        self.course_type = self.ui1.radioButton.isChecked()
        self.class_num = self.ui1.lineEdit.text()
        self.spc_time = self.ui1.lineEdit_2.text()
        self.spc_courses = self.ui1.lineEdit_3.text()
        self.cookie = self.ui1.lineEdit_4.text()
        # self.fetch_interval = float(self.ui1.lineEdit_5.text())
        self.fetch_timeout = float(self.ui1.lineEdit_6.text())
        self.text_browser.setText('已保存修改')
        self.text_browser.repaint()

    def launch(self):
        self.text_browser_2.setText('已启动定时抢课')
        self.text_browser_2.repaint()
        settings = {
            'Type': self.course_type,
            'ClassNum': self.class_num,
            'Cookie': self.cookie,
            'Time': self.spc_time,
            'Expected': self.spc_courses,
            # 'Interval': self.fetch_interval,
            'Timeout': self.fetch_timeout
        }
        print(settings)
        self.fecth_thread = FecthThread(settings)
        self.fecth_thread.data_fetched.connect(self.update_fetched_data)
        self.fecth_thread.start()

    def update_fetched_data(self, data):
        self.fetched_data = data  # 保存数据

        # 获取字典的键作为表头
        keys = self.fetched_data[0].keys()
        columns = ['课程名', '上课教师', '学分', '类型', '剩余']
        self.table_widget.setColumnCount(len(columns))
        self.table_widget.setHorizontalHeaderLabels(columns)

        # 设置行数
        self.table_widget.setRowCount(len(self.fetched_data))

        # 填充数据
        for row_index, item in enumerate(self.fetched_data):
            for col_index, key in enumerate(keys):
                self.table_widget.setItem(row_index, col_index, QTableWidgetItem(str(item[key])))

        # 设置列宽
        column_widths = [340, 100, 50, 50, 60]  # 用于示例的列宽，可以按需调整
        for col_index, width in enumerate(column_widths):
            if col_index < len(keys):  # 确保不超出范围
                self.table_widget.setColumnWidth(col_index, width)

    def confirm(self):
        self.text_browser_2.setText('确认')
        self.text_browser_2.repaint()
        # 获取当前选择的行索引
        selected_row = self.table_widget.currentRow()

        if selected_row != -1:  # 确保有选中的行
            # 提取该行的数据
            print(selected_row)
            print(f'选中第{selected_row + 1}行的数据:', self.fetched_data[selected_row])
            # 抢课操作
            settings = {
                'Type': self.course_type,
                'ClassNum': self.class_num,
                'Cookie': self.cookie,
                'Time': self.spc_time,
                'Expected': self.spc_courses,
                # 'Interval': self.fetch_interval,
                'Timeout': self.fetch_timeout
            }
            self.select_thread = SelectThread(self.fetched_data[selected_row], settings)
            self.select_thread.start()
        else:
            print('没有选中任何行')

    def refresh(self):
        print('刷新')
        settings = {
            'Type': self.course_type,
            'ClassNum': self.class_num,
            'Cookie': self.cookie,
            'Time': self.spc_time,
            'Expected': self.spc_courses,
            # 'Interval': self.fetch_interval,
            'Timeout': self.fetch_timeout
        }
        self.refresh_thread = FecthThread2(settings)
        self.refresh_thread.data_fetched.connect(self.update_fetched_data)
        self.refresh_thread.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
