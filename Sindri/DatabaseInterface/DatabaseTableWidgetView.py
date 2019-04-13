import os

from PySide2 import QtWidgets
from PySide2.QtWidgets import QTableWidget, QLineEdit, QPushButton

import db
import db_utils


class DatabaseTableWidgetView:
    def __init__(
        self,
        tablewidget: QTableWidget,
        le_search: QLineEdit,
        btnSearchSubstance: QPushButton,
    ):
        self.tableWidget_searchSubstance = tablewidget
        self.le_searchSubstance = le_search
        self.dbfile = db.database_file
        self.btn_searchSubstance = btnSearchSubstance

        self.btn_searchSubstance.clicked.connect(self.search_substance)
        self.tableWidget_searchSubstance.itemSelectionChanged.connect(
            self.substance_selected
        )
        # 26 colunas
        self.col_headers = [
            "Formula",
            "Name",
            "CAS #",
            "Mol. Wt.",
            "Tfp [K]",
            "Tb [K]",
            "Tc [K]",
            "Pc [bar]",
            "Vc [cm3/mol]",
            "Zc",
            "Omega",
            "T range (Cp) [K]",
            "a0",
            "a1",
            "a2",
            "a3",
            "a4",
            "Cp IG",
            "Cp liq.",
            "Antoine A",
            "Antoine B",
            "Antoine C",
            "Pvp min [bar]",
            "Tmin [K]",
            "Pvp max [bar]",
            "Tmax [K]",
        ]

        self.tableWidget_searchSubstance.setHorizontalHeaderLabels(self.col_headers)
        header = self.tableWidget_searchSubstance.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)

        self.load_db()
        self.le_searchSubstance.setFocus()
        self.database_changed = False

    def load_db(self):
        # Abrir banco de dados
        if os.path.isfile(self.dbfile):
            self.show_full_db()
        else:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage("Database not found")
            error_dialog.exec_()
            raise Exception("Database not found")

    def show_full_db(self):
        try:
            query = "SELECT * FROM database"
            db.cursor.execute(query)
            results = db.cursor.fetchall()
            self.update_table_db(results)
        except:
            pass

    def update_table_db(self, results):
        self.tableWidget_searchSubstance.setRowCount(0)

        for row_number, row_data in enumerate(results):
            self.tableWidget_searchSubstance.insertRow(row_number)
            for col_number, data in enumerate(row_data):
                self.tableWidget_searchSubstance.setItem(
                    row_number, col_number, QtWidgets.QTableWidgetItem(str(data))
                )

    def get_row_values(self, n):
        row_values = []
        current_row = self.tableWidget_searchSubstance.currentRow()

        for i in range(n):
            item = self.tableWidget_searchSubstance.item(current_row, i).text()
            row_values.append(item)

        return row_values

    def substance_selected(self):
        current_row = self.tableWidget_searchSubstance.currentRow()
        if current_row >= 0:
            r = self.get_row_values(10)
            self.compound = db_utils.get_compound_properties(r[1], r[0])
            self.sname = self.compound.getName()
            self.sformula = self.compound.getFormula()
        return self.compound, self.sname, self.sformula

    def search_substance(self):
        substance_string_name = str(self.le_searchSubstance.text())
        if substance_string_name == "":
            self.show_full_db()
        else:
            try:
                # query = "SELECT * FROM database WHERE Name LIKE '%" + substance_string_name + "%'" + \
                #         " OR Formula LIKE '%" + substance_string_name + "%'" + \
                #         " OR `CAS #` LIKE '%" + substance_string_name + "%'"
                query = (
                    "SELECT * FROM database WHERE Name LIKE '"
                    + substance_string_name
                    + "%'"
                    + " OR Formula LIKE '"
                    + substance_string_name
                    + "%'"
                    + " OR `CAS #` LIKE '"
                    + substance_string_name
                    + "%'"
                )
                db.cursor.execute(query)
                results = db.cursor.fetchall()
                self.update_table_db(results)
            except:
                self.tableWidget_searchSubstance.setRowCount(0)

    def clear_search(self):
        self.le_searchSubstance.clear()
        self.le_searchSubstance.setFocus()