from typing import Optional, List, Any, Union
from datetime import datetime
from PySide6.QtCore import (
    Qt,
    Slot,
    QAbstractTableModel,
    QModelIndex,
    QSortFilterProxyModel,
    QEvent,
    QAbstractItemModel,
)
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QWidget,
    QMenuBar,
    QHeaderView,
    QVBoxLayout,
    QTableView,
    QCompleter,
    QStyleOptionViewItem,
    QStyledItemDelegate,
    QLineEdit,
)
import sys

from persist import PersistSet
from models import Entry


class MainWindow(QMainWindow):
    class BudgetTableView(QTableView):
        class CompleterDeligate(QStyledItemDelegate):
            def __init__(self, parent: QWidget):
                super().__init__(parent)
                self.completer: Optional[QCompleter] = None

            def createEditor(
                self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex
            ) -> QWidget:
                editor = QLineEdit(parent)
                self.completer = QCompleter(["foo", "bar", "baz"], editor)
                # editor.textEdited.connect(
                #     lambda text: self.completer.setCompletionPrefix("")
                #     if text == ""
                #     else None
                # )
                self.completer.setCompletionColumn(0)
                self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
                self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
                self.completer.setCompletionMode(
                    QCompleter.CompletionMode.PopupCompletion
                )
                self.completer.setCompletionRole(Qt.ItemDataRole.EditRole)
                editor.setCompleter(self.completer)
                self.completer.complete()
                return editor

            # def editorEvent(
            #     self,
            #     event: QEvent,
            #     model: QAbstractItemModel,
            #     option: QStyleOptionViewItem,
            #     index: QModelIndex,
            # ) -> bool:
            #     print(event.type())
            #     if event.type() == QEvent.Type.MouseButtonRelease and self.completer:
            #         self.completer.complete()
            #     return super().editorEvent(event, model, option, index)

        def __init__(self, parent: QWidget):
            super().__init__(parent)
            # self.setEditTriggers(QAbstractItemView.NoEditTriggers)
            # self.setSelectionBehavior(QAbstractItemView.SelectRows)
            # self.setSelectionMode(QAbstractItemView.SingleSelection)
            self.setShowGrid(False)
            self.setSortingEnabled(True)
            self.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Interactive
            )
            self.verticalHeader().hide()
            self.setAlternatingRowColors(True)
            self.setSortingEnabled(True)
            self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
            self.setContextMenuPolicy(Qt.CustomContextMenu)
            # self.customContextMenuRequested.connect(self.context_menu)
            self.resizeColumnsToContents()
            self.resizeRowsToContents()

            # completer = QCompleter(["foo", "bar", "baz"], self)
            # completer.setCompletionColumn(2)
            # completer.setCaseSensitivity(Qt.CaseInsensitive)
            # completer.setFilterMode(Qt.MatchContains)
            # completer.setCompletionMode(QCompleter.PopupCompletion)
            # completer.setCompletionRole(Qt.EditRole)
            self.setItemDelegateForColumn(1, self.CompleterDeligate(self))

    class BudgetTableProxyModel(QSortFilterProxyModel):
        def __init__(self, parent: QWidget):
            super().__init__(parent)
            self.setFilterCaseSensitivity(Qt.CaseInsensitive)
            self.setFilterKeyColumn(-1)

    class BudgetTableModel(QAbstractTableModel):
        def __init__(self, parent: QWidget, budget_data: PersistSet[Entry]):
            super().__init__(parent)
            self.table_data: List[List[Any]] = []
            self.budget_data = budget_data
            for entry in self.budget_data:
                self.add_entry(entry)
            self.header_data = ["Date", "Category", "Sub-Category", "Code", "Amount"]

        def flags(self, index: QModelIndex):
            return (
                Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsSelectable
                | (
                    Qt.ItemFlag.ItemIsEditable
                    if index.column() == 1 or index.column() == 2
                    else Qt.ItemFlag.NoItemFlags
                )
            )

        def setData(
            self, index: QModelIndex, value: Any, role: int = Qt.ItemDataRole.EditRole
        ):
            if role == Qt.ItemDataRole.EditRole:
                self.table_data[index.row()][index.column()] = value
                self.dataChanged.emit(index, index)
                self.budget_data.add(
                    Entry(
                        date=datetime.strptime(
                            self.table_data[index.row()][0], "%Y-%m-%d"
                        ),
                        category=self.table_data[index.row()][1],
                        sub_category=self.table_data[index.row()][2],
                        bank_code=self.table_data[index.row()][3],
                        amount=float(self.table_data[index.row()][4][1:])
                        if self.table_data[index.row()][4][0] == "$"
                        else -float(self.table_data[index.row()][4][2:]),
                    )
                )
                # for entry in self.budget_data.data:
                #     print(entry)
                return True
            return False

        #     self.horizontalHeader().setSectionResizeMode(
        #         QHeaderView.ResizeMode.ResizeToContents
        #     )
        #     self.verticalHeader().hide()

        @Slot(Entry)
        def add_entry(self, entry: Entry):
            row: List[Any] = [
                entry.date.strftime("%Y-%m-%d"),
                entry.category,
                entry.sub_category,
                entry.bank_code,
                f"${entry.amount:.2f}"
                if entry.amount >= 0
                else f"-${-entry.amount:.2f}",
            ]
            self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
            self.table_data.append(row)
            self.endInsertRows()

        def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
            if role == Qt.ItemDataRole.DisplayRole:
                return self.table_data[index.row()][index.column()]
            return None

        def headerData(
            self,
            section: int,
            orientation: Qt.Orientation,
            role: int = Qt.ItemDataRole.DisplayRole,
        ) -> Optional[str]:
            if (
                role == Qt.ItemDataRole.DisplayRole
                and orientation == Qt.Orientation.Horizontal
            ):
                return self.header_data[section]
            return None

        def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
            return 5

        def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
            return len(self.table_data)

    def __init__(self):
        super().__init__()
        super().setObjectName("main_window")

        self.budget_data = PersistSet[Entry]("budget_data")

        self.setWindowTitle("Budget App")
        self.setMinimumSize(800, 600)

        self.main_widget = QWidget(self)
        self.main_widget.setObjectName("main_widget")
        self.setCentralWidget(self.main_widget)

        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setObjectName("main_layout")

        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)
        self.load_csv_action = self.menu_bar.addAction("Load CSV")
        self.menu_bar.addAction(self.load_csv_action)
        self.load_csv_action.triggered.connect(self.load_csv)

        self.budget_table_model = self.BudgetTableModel(self, self.budget_data)
        self.budget_table_model.setObjectName("budget_table_model")
        self.budget_table_proxy_model = self.BudgetTableProxyModel(self)
        self.budget_table_proxy_model.setSourceModel(self.budget_table_model)
        self.budget_table_proxy_model.setObjectName("budget_table_proxy_model")
        self.budget_table_view = self.BudgetTableView(self)
        self.budget_table_view.setObjectName("budget_table_view")
        self.budget_table_view.setModel(self.budget_table_proxy_model)
        self.main_layout.addWidget(self.budget_table_view)

    @Slot()
    def load_csv(self):
        # file_name = QFileDialog.getOpenFileName(
        #     self, "Open CSV", "", "CSV Files (*.csv)"
        # )
        file_name = [
            r"C:\Users\t.moore\Downloads\01-0676-0332021-00_Transactions_2023-01-01_2023-01-31.csv"
        ]
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
                self.budget_table_model.add_entry(entry)
                self.budget_table_view.resizeColumnsToContents()
                self.budget_table_view.resizeRowsToContents()
                self.budget_table_view.sortByColumn(0, Qt.SortOrder.AscendingOrder)
                self.budget_data.add(entry)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec())
