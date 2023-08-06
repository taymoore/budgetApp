from typing import List
from datetime import datetime
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QWidget,
    QMenuBar,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)
import sys

from persist import PersistSet
from models import Entry


class MainWindow(QMainWindow):
    class BudgetTable(QTableWidget):
        def __init__(self, parent: QWidget):
            super().__init__(parent)
            self.setColumnCount(5)
            self.setRowCount(0)
            self.setHorizontalHeaderLabels(
                ["Date", "Category", "Sub-Category", "Code", "Amount"]
            )
            self.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.ResizeToContents
            )
            self.verticalHeader().hide()

        @Slot(Entry)
        def add_entry(self, entry: Entry):
            row: List[QTableWidgetItem] = [
                QTableWidgetItem(entry.date.strftime("%Y-%m-%d")),
                QTableWidgetItem(entry.category),
                QTableWidgetItem(entry.sub_category),
                QTableWidgetItem(entry.bank_code),
                QTableWidgetItem(str(entry.amount)),
            ]
            self.insertRow(self.rowCount())
            self.setItem(self.rowCount() - 1, 0, row[0])
            self.setItem(self.rowCount() - 1, 1, row[1])
            self.setItem(self.rowCount() - 1, 2, row[2])
            self.setItem(self.rowCount() - 1, 3, row[3])
            self.setItem(self.rowCount() - 1, 4, row[4])
            # self.setRowHeight(self.rowCount() - 1, 20)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Budget App")
        self.setMinimumSize(800, 600)

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)

        self.main_layout = QVBoxLayout(self)
        self.main_widget.setLayout(self.main_layout)

        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)
        self.load_csv_action = self.menu_bar.addAction("Load CSV")
        self.menu_bar.addAction(self.load_csv_action)
        self.load_csv_action.triggered.connect(self.load_csv)

        self.budget_table = self.BudgetTable(self)
        self.main_layout.addWidget(self.budget_table)

        self.budget_data = PersistSet[Entry]("budget_data")

    @Slot()
    def load_csv(self):
        file_name = QFileDialog.getOpenFileName(
            self, "Open CSV", "", "CSV Files (*.csv)"
        )
        if file_name[0] == "":
            return
        with open(file_name[0]) as f:
            for line in f:
                type, details, _, code, _, amount, date, _, _ = line.split(",")
                if type == "Visa Purchase":
                    entry = Entry(
                        bank_code=code,
                        category="",
                        sub_category="",
                        amount=amount,
                        date=datetime.strptime(date, "%d/%m/%Y"),
                    )
                else:
                    continue
                self.budget_table.add_entry(entry)
                self.budget_data.add(entry)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec())
