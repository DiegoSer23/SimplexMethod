import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLineEdit, QLabel, QComboBox, QMessageBox, \
    QTableWidget, QTableWidgetItem, QCheckBox, QDialog
from  PyQt5.QtGui import QColor
from PyQt5.QtCore import pyqtSlot
import numpy as np

# Global variables
status = 0
numvar = 0
numrest = 0
current_iteration = 0
phase1_done = False
matrix = None
arrayobj = None
arrayart = []
art_vert_header = []
art_hor_header = []
signslist = []
rhs = []
variables = []
objfun = ""
hasartvar = False
min_done = False
numcolumns = 0


class SimplexWindow(QMainWindow):

    num_equ = 0
    ar_column = []

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Algoritmo Simplex")
        self.setGeometry(100, 100, 1000, 675)
        self.setFixedSize(1000, 675)
        self.firstime = True
        # Initialize label for variables
        labelvar = QLabel(self)
        labelvar.setText('Ingresa el número de variables de decisión: ')
        labelvar.adjustSize()
        # Initialize label for restrictions
        labelrest = QLabel(self)
        labelrest.setText('Ingresa el número de restricciones: ')
        labelrest.adjustSize()
        # Initialize label for selecting max/min
        labelobj = QLabel(self)
        labelobj.setText('Selecciona el objetivo de la función: ')
        labelobj.adjustSize()
        # Initialize label for iterations
        self.iteration_lbl = QLabel(self)
        self.iteration_lbl.setText('Ingresar restricciones:')
        self.iteration_lbl.adjustSize()
        # Best label
        label_nam = QLabel(self)
        label_nam.setText('Programa creado por: Diego Servín Noguez')
        label_nam.adjustSize()
        # Initialize label for objective function
        labelit = QLabel(self)
        labelit.setText('Ingresar valores función objetivo:')
        labelit.adjustSize()
        # Initialize line edits
        self.vartext = QLineEdit(self)
        self.vartext.setMaxLength(2)
        self.resttext = QLineEdit(self)
        self.resttext.setMaxLength(2)
        # Initialize combobox
        self.objective = QComboBox(self)
        self.objective.addItem("Max Z")
        self.objective.addItem("Min Z")
        # Initialize radio buttons for iterations options
        self.one_iteration = QCheckBox("Última iteración", self)
        self.one_iteration.setChecked(False)
        self.one_iteration.adjustSize()
        self.one_iteration.toggled.connect(lambda: self.alternate_options(self.one_iteration))
        self.all_iterations = QCheckBox("Todas las iteraciones", self)
        self.all_iterations.setChecked(True)
        self.all_iterations.adjustSize()
        self.all_iterations.toggled.connect(lambda: self.alternate_options(self.all_iterations))
        # Initialize objective function table
        self.objfunction = QTableWidget(self)
        self.objfunction.setMinimumHeight(85)
        self.objfunction.setMaximumHeight(85)
        self.objfunction.setMaximumWidth(750)
        self.objfunction.setMinimumWidth(750)
        # Initialize user table restrictions
        self.table = QTableWidget(self)
        self.table.setMinimumWidth(900)
        self.table.setMaximumWidth(900)
        self.table.setMaximumHeight(350)
        self.table.setMinimumHeight(350)
        # Initialize reset button
        self.reset = QPushButton('Reiniciar', self)
        self.reset.setToolTip('Reiniciar ingreso de datos')
        self.reset.clicked.connect(lambda: self.reset_all())
        self.reset.adjustSize()
        self.reset.hide()
        # Initialize button for analysis window
        self.button_analysis = QPushButton('Análisis sensibilidad', self)
        self.button_analysis.setToolTip('Mostrar análisis de resultados')
        self.button_analysis.clicked.connect(lambda: self.call_window())
        self.button_analysis.adjustSize()
        self.button_analysis.hide()
        # Initialize button for results
        self.button_results = QPushButton('Resultados', self)
        self.button_results.setToolTip('Mostrar resultados')
        self.button_results.clicked.connect(lambda: self.show_results())
        self.button_results.hide()
        self.button_results.adjustSize()
        # Initialize confirm objective function
        self.button_obj_confirm = QPushButton('Confirmar función', self)
        self.button_obj_confirm.setToolTip('Confirmar función objetivo')
        self.button_obj_confirm.clicked.connect(lambda: self.validate_obj_function())
        self.button_obj_confirm.adjustSize()
        # Initialize restrictions confirm button
        self.button_restrict_confirm = QPushButton('Confirmar restricciones', self)
        self.button_restrict_confirm.setToolTip('Confirmar restricciones')
        self.button_restrict_confirm.clicked.connect(lambda: self.validate_restrictions())
        self.button_restrict_confirm.adjustSize()
        # Initialize confirm button
        self.button_confirm = QPushButton('Confirmar', self)
        self.button_confirm.setToolTip('Confirmar datos')
        self.button_confirm.clicked.connect(lambda: self.validate_variables())
        # Initialize next iteration button
        self.button_next = QPushButton('->', self)
        self.button_next.setToolTip('Siguiente iteración')
        self.button_next.clicked.connect(lambda: self.next_iteration())
        self.button_next.hide()
        # Initialize message box
        self.message = QMessageBox(self)
        # Deactivate buttons
        self.button_restrict_confirm.setEnabled(False)
        self.button_obj_confirm.setEnabled(False)
        # Setting up components
        label_nam.move(50, 25)
        labelvar.move(50, 50)
        self.vartext.move(50, 75)
        labelrest.move(350, 50)
        self.resttext.move(350, 75)
        labelobj.move(575, 50)
        self.objective.move(575, 75)
        self.button_results.move(800, 630)
        self.button_analysis.move(650, 630)
        self.reset.move(200, 630)
        self.button_confirm.move(800, 75)
        self.button_restrict_confirm.move(50, 630)
        self.button_obj_confirm.move(830, 190)
        self.button_next.move(450, 630)
        self.one_iteration.move(450, 250)
        self.all_iterations.move(600, 250)
        labelit.move(50, 125)
        self.table.move(50, 275)
        self.objfunction.move(50, 150)
        self.iteration_lbl.move(50, 245)
        self.show()

    # Validate if the line edits are not empty and numbers, display error messages, create both table views
    @pyqtSlot()
    def validate_variables(self):
        if self.is_empty_vars() or self.is_empty_rest():
            self.message.setIcon(QMessageBox.Critical)
            self.message.setText('Hay campos que no han sido llenados.')
            self.message.setWindowTitle('Error')
            self.message.exec()
        else:
            if self.is_int(self.vartext.text()) and self.is_int(self.resttext.text()):
                if int(self.vartext.text()) <= 0 or int(self.resttext.text()) <= 0 or int(self.vartext.text()) > 20 or \
                        int(self.resttext.text()) > 20:
                    self.message.setIcon(QMessageBox.Critical)
                    self.message.setText('Las restricciones ni las variables pueden ser menores a cero o mayores a 20.')
                    self.message.setWindowTitle('Error')
                    self.message.exec()
                else:
                    global numvar, numrest, numcolumns, arrayobj, objfun
                    numvar = int(self.vartext.text())
                    numrest = int(self.resttext.text())
                    numcolumns = numvar + 1
                    objfun = str(self.objective.currentText())
                    arrayobj = np.zeros(shape=(1, numvar))
                    self.objfunction.setRowCount(1)
                    self.objfunction.setColumnCount(numvar)
                    self.init_table_obj()
                    self.table.setRowCount(numrest)
                    self.table.setColumnCount(numvar+2)
                    self.init_table_edit()
                    self.button_obj_confirm.setEnabled(True)
                    self.button_restrict_confirm.setEnabled(False)
                    self.objfunction.setEnabled(True)
                    self.table.setEnabled(False)
                    self.button_confirm.setEnabled(False)
                    self.vartext.setEnabled(False)
                    self.resttext.setEnabled(False)
                    self.objective.setEnabled(False)

            else:
                self.message.setIcon(QMessageBox.Critical)
                self.message.setText('Ingresar sólo números enteros en los campos.')
                self.message.setWindowTitle('Error')
                self.message.exec()

    # Check if the input is only a int
    @staticmethod
    def is_int(number):
        try:
            int(number)
            return True
        except ValueError:
            return False

    # Validate if the line edit is not empty or with spaces
    def is_empty_vars(self):
        if self.vartext.text().isspace() or self.vartext.text() == "":
            return True
        else:
            return False

    # Validate if the line edit is not empty or with spaces
    def is_empty_rest(self):
        if self.resttext.text().isspace() or self.vartext.text() == "":
            return True
        else:
            return False

    # Create the table for the user to edit restrictions
    def init_table_edit(self):
        headers = ""
        for x in range(numvar):
            headers += "X"
            headers += str(x+1)
            headers += ";"
        headers += "Desigualdad;Limitante"
        self.table.setHorizontalHeaderLabels(headers.split(";"))
        stylesheet = "::section{Background-color:rgb(0,196,255);border-radius:14px;}"
        self.table.horizontalHeader().setStyleSheet(stylesheet)
        for row in range(numrest):
            for column in range(numcolumns + 1):
                if column < numvar:
                    self.table.setItem(row, column, QTableWidgetItem(str(0.0)))
                if column == numvar:
                    self.table.setItem(row, column, QTableWidgetItem('<='))
                if column == numvar + 1:
                    self.table.setItem(row, column, QTableWidgetItem(str(0.0)))

    # Create table for user objective function
    def init_table_obj(self):
        header = ""
        for x in range(numvar):
            header += "X" + str(x+1) + ";"
        header = header[:-1]
        self.objfunction.setHorizontalHeaderLabels(header.split(";"))
        stylesheet = "::section{Background-color:rgb(0,255,145);border-radius:14px;}"
        self.objfunction.horizontalHeader().setStyleSheet(stylesheet)

    # Validate restrictions and save them for further use
    @pyqtSlot()
    def validate_restrictions(self):
        global numcolumns, matrix, hasartvar, art_vert_header, arrayart, rhs, variables
        neg_row = []
        art_vert_header.append("Z")
        num_eq = 0
        h = 1
        e = 1
        a = 1
        # First we save the signs and if one is incorrect we delete what we had saved
        for row in range(numrest):
            if self.table.item(row, numvar).text() == "<=":
                if self.is_float(self.table.item(row, numvar+1).text()):
                    if float(self.table.item(row, numvar+1).text()) < 0:
                        hasartvar = True
                        numcolumns = numcolumns + 2
                        art_hor_header.append("E" + str(e))
                        art_hor_header.append("A" + str(a))
                        art_vert_header.append("A" + str(a))
                        variables.append("E" + str(e))
                        arrayart.append(row + 1)
                        e += 1
                        a += 1
                        signslist.append(">=")
                        neg_row.append(row + 1)
                    else:
                        numcolumns = numcolumns + 1
                        art_hor_header.append("H" + str(h))
                        art_vert_header.append("H" + str(h))
                        variables.append("H" + str(h))
                        h += 1
                        signslist.append(self.table.item(row, numvar).text())
                else:
                    self.message.setIcon(QMessageBox.Critical)
                    self.message.setText('Sólo ingresar números decimales para el lado derecho.')
                    self.message.setWindowTitle('Error')
                    self.message.exec()
                    numcolumns = numvar + 1
                    hasartvar = False
                    arrayart.clear()
                    signslist.clear()
                    art_hor_header.clear()
                    art_vert_header.clear()
                    variables.clear()
            else:
                if self.table.item(row, numvar).text() == ">=":
                    if self.is_float(self.table.item(row, numvar+1).text()):
                        if float(self.table.item(row, numvar + 1).text()) < 0:
                            numcolumns = numcolumns + 1
                            art_hor_header.append("H" + str(h))
                            art_vert_header.append("H" + str(h))
                            variables.append("H" + str(h))
                            h += 1
                            signslist.append("<=")
                            neg_row.append(row + 1)
                        else:
                            hasartvar = True
                            numcolumns = numcolumns + 2
                            art_hor_header.append("E" + str(e))
                            art_hor_header.append("A" + str(a))
                            art_vert_header.append("A" + str(a))
                            variables.append("E" + str(e))
                            arrayart.append(row + 1)
                            e += 1
                            a += 1
                            signslist.append(self.table.item(row, numvar).text())
                    else:
                        self.message.setIcon(QMessageBox.Critical)
                        self.message.setText('Sólo ingresar números decimales para el lado derecho.')
                        self.message.setWindowTitle('Error')
                        self.message.exec()
                        numcolumns = numvar + 1
                        hasartvar = False
                        arrayart.clear()
                        signslist.clear()
                        art_hor_header.clear()
                        art_vert_header.clear()
                        variables.clear()
                else:
                    if self.table.item(row, numvar).text() == "=":
                        hasartvar = True
                        numcolumns = numcolumns + 1
                        art_hor_header.append("*A"+str(a))
                        art_vert_header.append("*A"+str(a))
                        variables.append("A"+str(a))
                        a += 1
                        arrayart.append(row + 1)
                        signslist.append(self.table.item(row, numvar).text())
                        num_eq += 1
                        if self.is_float(self.table.item(row, numvar + 1).text()):
                            if float(self.table.item(row, numvar + 1).text()) < 0:
                                neg_row.append(row + 1)
                        else:
                            self.message.setIcon(QMessageBox.Critical)
                            self.message.setText('Sólo ingresar números decimales para el lado derecho.')
                            self.message.setWindowTitle('Error')
                            self.message.exec()
                            numcolumns = numvar + 1
                            hasartvar = False
                            arrayart.clear()
                            signslist.clear()
                            art_hor_header.clear()
                            art_vert_header.clear()
                            variables.clear()
                    else:
                        self.message.setIcon(QMessageBox.Critical)
                        self.message.setText('Sólo ingresar "<=", ">=" ó "=" en las desigualdades.')
                        self.message.setWindowTitle('Error')
                        self.message.exec()
                        numcolumns = numvar + 1
                        hasartvar = False
                        arrayart.clear()
                        signslist.clear()
                        art_hor_header.clear()
                        art_vert_header.clear()
                        variables.clear()
                        for x in range(numvar):
                            art_hor_header.append("X" + str(x + 1))
                        return
        art_hor_header.append("Solución")
        # We create the matrix taking into account slack and surplus variables
        matrix = np.zeros(shape=(numrest+1, numcolumns))
        SimplexWindow.num_equ = num_eq
        all_valid = False
        for row in range(numrest):
            for column in range(numvar):
                if self.is_float(self.table.item(row, column).text()):
                    if row == numrest-1 and column == numvar-1:
                        all_valid = True
                else:
                    self.message.setIcon(QMessageBox.Critical)
                    self.message.setText('Sólo ingresar números decimales para el valor de las variables.')
                    self.message.setWindowTitle('Error')
                    self.message.exec()
                    numcolumns = numvar + 1
                    hasartvar = False
                    arrayart.clear()
                    signslist.clear()
                    art_hor_header.clear()
                    art_vert_header.clear()
                    variables.clear()
                    for x in range(numvar):
                        art_hor_header.append("X" + str(x + 1))
                    return
        all_valid_limit = False
        for row in range(numrest):
            if self.is_float(self.table.item(row, numvar+1).text()):
                if row == numrest-1:
                    all_valid_limit = True
            else:
                self.message.setIcon(QMessageBox.Critical)
                self.message.setText('Sólo ingresar números decimales para el valor del lado derecho.')
                self.message.setWindowTitle('Error')
                self.message.exec()
                numcolumns = numvar + 1
                hasartvar = False
                arrayart.clear()
                signslist.clear()
                art_hor_header.clear()
                art_vert_header.clear()
                variables.clear()
                for x in range(numvar):
                    art_hor_header.append("X" + str(x + 1))
                return
        # We fill matrix with normal restrictions
        if all_valid and all_valid_limit:
            extra = numvar
            r = 1
            for var in range(numvar):
                matrix[0, var] = arrayobj[0, var] * -1
            while r < numrest+1:
                for c in range(numvar):
                    matrix[r, c] = float(self.table.item(r-1, c).text())
                if signslist[r-1] == "<=":
                    matrix[r, extra] = 1
                    extra += 1
                else:
                    if signslist[r-1] == ">=":
                        matrix[r, extra] = -1
                        extra += 1
                        matrix[r, extra] = 1
                        matrix[0, extra] = 1
                        extra += 1
                    else:
                        if signslist[r-1] == "=":
                            matrix[r, extra] = 1
                            matrix[0, extra] = 1
                            extra += 1
                matrix[r, numcolumns-1] = float(self.table.item(r-1, numvar+1).text())
                rhs.append(float(self.table.item(r - 1, numvar + 1).text()))
                r += 1
            for x in range(len(neg_row)):
                matrix[neg_row[x], :] *= -1
        self.table.setEnabled(False)
        self.button_restrict_confirm.setEnabled(False)
        self.one_iteration.setEnabled(False)
        self.all_iterations.setEnabled(False)
        self.button_results.show()

    # Check if signs are correct
    @staticmethod
    def check_signs(sign):
        if sign == "<=" or sign == ">=" or sign == "=":
            return True
        else:
            return False

    # Check if it is a float number
    @staticmethod
    def is_float(number):
        try:
            float(number)
            return True
        except ValueError:
            return False

    # Function for saving objective function
    @pyqtSlot()
    def validate_obj_function(self):
        global arrayobj, objfun
        all_valid = False
        # First check if all values are floats
        for column in range(numvar):
            if self.objfunction.item(0, column):
                if self.is_float(self.objfunction.item(0, column).text()):
                    if float(self.objfunction.item(0, column).text()) == 0:
                        self.message.setIcon(QMessageBox.Critical)
                        self.message.setText('No puede haber valores de cero en la función objetivo.')
                        self.message.setWindowTitle('Error')
                        self.message.exec()
                        return
                    if column == numvar - 1:
                        all_valid = True
                else:
                    self.message.setIcon(QMessageBox.Critical)
                    self.message.setText('Sólo ingresar números decimales para el valor de las variables.')
                    self.message.setWindowTitle('Error')
                    self.message.exec()
                    return
            else:
                self.message.setIcon(QMessageBox.Critical)
                self.message.setText('Llenar todos los campos.')
                self.message.setWindowTitle('Error')
                self.message.exec()
                return
        # When all are floats we save them in an array
        if all_valid:
            all_neg = False
            mult = 1
            for neg in range(numvar):
                if float(self.objfunction.item(0, neg).text()) == 0:
                    self.message.setIcon(QMessageBox.Critical)
                    self.message.setText('No debe haber coeficientes en 0 en la función objetivo.')
                    self.message.setWindowTitle('Error')
                    self.message.exec()
                    return
                else:
                    if float(self.objfunction.item(0, neg).text()) < 0:
                        if neg == numvar - 1:
                            all_neg = True
                    else:
                        break
            if all_neg:
                mult = -1
                if objfun == "Max Z":
                    objfun = "Min Z"
                else:
                    objfun = "Max Z"
            for x in range(numvar):
                art_hor_header.append("X"+str(x+1))
                arrayobj[0, x] = float(self.objfunction.item(0, x).text()) * mult
            self.button_obj_confirm.setEnabled(False)
            self.objfunction.setEnabled(False)
            self.table.setEnabled(True)
            self.button_restrict_confirm.setEnabled(True)

    @pyqtSlot()
    def show_results(self):
        global current_iteration, matrix, status
        if self.one_iteration.isChecked():
            if hasartvar:
                for column in range(numvar):
                    matrix[0, column] = 0
                for column in range(numcolumns):
                    sumlines = 0
                    for row in range(len(arrayart)):
                        sumlines += matrix[arrayart[row], column]
                    sumlines *= -1
                    matrix[0, column] += sumlines
                while not phase1_done and status != -1 and status != -2:
                    self.solve_phase1()
                if status == -1:
                    self.no_solution()
                    self.button_results.setEnabled(False)
                    self.table.setEnabled(True)
                    self.show_iteration()
                    self.reset.show()
                    return
                if status == -2:
                    self.unbounded_solution()
                    self.button_results.setEnabled(False)
                    self.table.setEnabled(True)
                    self.show_iteration()
                    self.reset.show()
                    return
                if phase1_done:
                    while not self.eliminate_artificial_var():
                        pass
                    self.add_objectivefunc()
                    if objfun == "Max Z":
                        while status != 1 and status != -2 and status != 2:
                            self.solve_max()
                    else:
                        self.solve_min()
                        while status != 1 and status != -2 and status != 2:
                            self.solve_max()
                    # We check which solution it is
                    if status == -2:
                        self.unbounded_solution()
                        self.button_results.setEnabled(False)
                        self.table.setEnabled(True)
                        self.show_iteration()
                        self.reset.show()
                        return
                    if status == 2:
                        self.infinite_solutions()
                        self.button_results.setEnabled(False)
                        self.table.setEnabled(True)
                        self.show_iteration()
                        self.reset.show()
                        return
                    if status == 1:
                        self.optimal_solution()
                        self.button_results.setEnabled(False)
                        self.table.setEnabled(True)
                        self.button_analysis.show()
                        self.show_iteration()
                        self.reset.show()
                        return
            else:
                if objfun == "Max Z":
                    while status != 1 and status != -2 and status != 2:
                        self.solve_max()
                else:
                    self.add_objectivefunc()
                    while status != 1 and status != -2 and status != 2:
                        self.solve_max()
                # Solutions
                if status == -2:
                    self.unbounded_solution()
                    self.button_results.setEnabled(False)
                    self.table.setEnabled(True)
                    self.show_iteration()
                    self.reset.show()
                    return
                if status == 2:
                    self.infinite_solutions()
                    self.button_results.setEnabled(False)
                    self.table.setEnabled(True)
                    self.show_iteration()
                    self.reset.show()
                    return
                if status == 1:
                    self.optimal_solution()
                    self.button_results.setEnabled(False)
                    self.table.setEnabled(True)
                    self.button_analysis.show()
                    self.show_iteration()
                    self.reset.show()
                    return
        else:
            self.iteration_lbl.setText("Iteración 0")
            self.show_iteration()
            self.button_next.show()
        self.button_results.setEnabled(False)
        self.table.setEnabled(True)

    @pyqtSlot()
    def next_iteration(self):
        global current_iteration, matrix
        if hasartvar and current_iteration == 0:
            for column in range(numvar):
                matrix[0, column] = 0
            self.show_iteration()
            current_iteration += 1
            self.iteration_lbl.setText("Iniciamos fase 1 quitando función objetivo")
            self.iteration_lbl.adjustSize()
            return
        if hasartvar and current_iteration == 1:
            current_iteration += 1
            for column in range(numcolumns):
                sumlines = 0
                for row in range(len(arrayart)):
                    sumlines += matrix[arrayart[row], column]
                sumlines *= -1
                matrix[0, column] += sumlines
                self.iteration_lbl.setText("Eliminamos las variables artificiales con la suma de filas")
                self.iteration_lbl.adjustSize()
        else:
            if hasartvar:
                if not phase1_done:
                    self.solve_phase1()
                else:
                    if self.firstime:
                        self.iteration_lbl.setText("Metemos la función objetivo de nuevo al inicio fase 2")
                        self.iteration_lbl.adjustSize()
                        self.add_objectivefunc()
                        self.firstime = False
                    else:
                        if objfun == "Max Z":
                            self.solve_max()
                        else:
                            if not min_done:
                                self.solve_min()
                            else:
                                self.solve_max()
            else:
                if objfun == "Max Z":
                    self.solve_max()
                else:
                    self.add_objectivefunc()
                    self.solve_max()
        if status == 1:
            self.optimal_solution()
            self.button_analysis.show()
            self.reset.show()
            return
        if status == 2:
            self.infinite_solutions()
            self.reset.show()
            return
        if status == -1:
            self.no_solution()
            self.reset.show()
            return
        if status == -2:
            self.unbounded_solution()
            self.reset.show()
            return
        self.show_iteration()

    def show_iteration(self):
        self.table.setColumnCount(numcolumns)
        self.table.setRowCount(numrest + 1)
        self.table.setHorizontalHeaderLabels(art_hor_header)
        self.table.setVerticalHeaderLabels(art_vert_header)
        stylesheet = "::section{Background-color:rgb(0,255,145);border-radius:14px;}"
        self.table.horizontalHeader().setStyleSheet(stylesheet)
        stylesheet = "::section{Background-color:rgb(100,200,145);border-radius:14px;}"
        self.table.verticalHeader().setStyleSheet(stylesheet)
        for row in range(numrest + 1):
            for column in range(numcolumns):
                item = QTableWidgetItem()
                item.setText(str(round(matrix[row, column], 4)))
                self.table.setItem(row, column, item)

    def solve_max(self):
        global status, matrix, status, current_iteration
        end = False
        if objfun == "Max Z":
            for column in range(numcolumns):
                check = art_hor_header[column]
                if check.startswith('*'):
                    continue
                if round(matrix[0, column], 4) >= 0:
                    if column == numcolumns - 1:
                        end = True
                else:
                    break
        else:
            for column in range(numcolumns):
                check = art_hor_header[column]
                if check.startswith('*'):
                    continue
                if column == numcolumns - 1:
                    end = True
                if round(matrix[0, column], 4) >= 0:
                    continue
                else:
                    break
        if end:
            status = 1
            if self.has_infinite_solutions():
                status = 2
            return
        # First we find the pivot column
        self.iteration_lbl.setText("Iteración " + str(current_iteration))
        current_iteration += 1
        max_neg = 0
        pivot_column = 0
        pivot_row = 0
        for column in range(numcolumns-1):
            check = art_hor_header[column]
            if round(matrix[0, column], 4) < 0 and not check.startswith('*'):
                if abs(round(matrix[0, column], 4)) > max_neg:
                    max_neg = abs(matrix[0, column])
                    pivot_column = column
        # Check if it is unbounded
        is_unbounded = False
        for row in range(numrest+1):
            if row > 0:
                if round(matrix[row, pivot_column], 4) <= 0:
                    if row == numrest:
                        is_unbounded = True
                else:
                    break
        if is_unbounded:
            status = -2
            return
        # Find pivot row
        min_row = -1
        for row in range(numrest+1):
            if row > 0:
                if round(matrix[row, pivot_column], 4) > 0 and round(matrix[row, numcolumns-1], 4) >= 0:
                    if min_row == -1:
                        min_row = matrix[row, numcolumns-1] / matrix[row, pivot_column]
                        pivot_row = row
                    else:
                        if round(matrix[row, numcolumns-1] / matrix[row, pivot_column], 4) <= round(min_row, 4):
                            if round(matrix[row, numcolumns-1] / matrix[row, pivot_column], 4) == round(min_row, 4):
                                check = art_vert_header[row]
                                if check.startswith('H') or check.startswith('E'):
                                    min_row = matrix[row, numcolumns - 1] / matrix[row, pivot_column]
                                    pivot_row = row
                            else:
                                min_row = matrix[row, numcolumns - 1] / matrix[row, pivot_column]
                                pivot_row = row
        matrix[pivot_row, :] *= 1 / matrix[pivot_row, pivot_column]
        # We convert all numbers to 0 above and below
        for row in range(numrest + 1):
            multiplier = matrix[row, pivot_column] * -1
            for column in range(numcolumns):
                if row != pivot_row:
                    if round(multiplier, 4) != 0:
                        matrix[row, column] += multiplier * matrix[pivot_row, column]
        # Change vertical header to variable that enter
        art_vert_header[pivot_row] = art_hor_header[pivot_column]

    @staticmethod
    def solve_min():
        global min_done, matrix
        for x in range(numvar):
            check = art_hor_header[x]
            if round(matrix[0, x], 4) > 0:
                multiplier = matrix[0, x] * -1
                for row in range(numrest+1):
                    if check == art_vert_header[row]:
                        for col in range(numcolumns):
                            matrix[0, col] += multiplier * matrix[row, col]
        min_done = True

    @staticmethod
    def eliminate_artificial_var():
        global matrix, numcolumns, art_hor_header
        columns = numcolumns
        for x in range(columns):
            check = art_hor_header[x]
            if check.startswith('A'):
                numcolumns -= 1
                matrix = np.delete(matrix, x, axis=1)
                art_hor_header.pop(x)
                return False
            if x == columns-1:
                return True

    @staticmethod
    def add_objectivefunc():
        global matrix
        for column in range(numvar):
            if objfun == "Max Z":
                matrix[0, column] = arrayobj[0, column] * -1
            else:
                matrix[0, column] = arrayobj[0, column] * -1 * -1

    @staticmethod
    def create_solution_string():
        if objfun == "Min Z":
            solution = round(matrix[0, numcolumns-1], 4) * -1
        else:
            solution = round(matrix[0, numcolumns-1], 4)
        string = "La solución óptima es Z=" + str(solution) + ", "
        for x in range(numvar):
            check = art_hor_header[x]
            for y in range(numrest + 1):
                if check == art_vert_header[y]:
                    string += check + "=" + str(round(matrix[y, numcolumns - 1], 4)) + ", "
                    break
                else:
                    if y == numrest:
                        string += check + "=" + str(0.0) + ", "
        string = string[:-2]
        return string

    def solve_phase1(self):
        global status, phase1_done, art_vert_header, art_hor_header, matrix, current_iteration
        # First we check if we haven't reach optimal solution
        end = False
        for column in range(numcolumns-1):
            if round(matrix[0, column], 4) >= 0:
                if column == numcolumns-2:
                    end = True
            else:
                break
        if end:
            if round(matrix[0, numcolumns-1], 4) != 0:
                status = -1
            else:
                phase1_done = True
                while not self.eliminate_artificial_var():
                    pass
                self.iteration_lbl.setText("Acaba fase 1 y eliminamos columnas artificiales")
                self.iteration_lbl.adjustSize()
                for x in range(numcolumns):
                    check = art_hor_header[x]
                    if check.startswith('*'):
                        matrix[0, x] = 0
            return
        # First we select pivot column
        self.iteration_lbl.setText("Iteración " + str(current_iteration))
        current_iteration += 1
        max_neg = 0
        pivot_column = 0
        pivot_row = 0
        for column in range(numcolumns-1):
            if round(matrix[0, column], 4) < 0:
                if abs(round(matrix[0, column], 4)) > max_neg:
                    max_neg = abs(matrix[0, column])
                    pivot_column = column
        # We can check if problem is unbounded
        is_unbounded = False
        for row in range(numrest+1):
            if row > 0:
                if round(matrix[row, pivot_column], 4) <= 0:
                    if row == numrest:
                        is_unbounded = True
                else:
                    break
        if is_unbounded:
            status = -2
            return
        # If it is not unbounded we select pivot row
        min_row = -1
        for row in range(numrest+1):
            if row > 0:
                if round(matrix[row, pivot_column], 4) > 0 and round(matrix[row, numcolumns-1], 4) >= 0:
                    if min_row == -1:
                        min_row = matrix[row, numcolumns-1] / matrix[row, pivot_column]
                        pivot_row = row
                    else:
                        if round(matrix[row, numcolumns-1] / matrix[row, pivot_column], 4) <= round(min_row, 4):
                            if round(matrix[row, numcolumns-1] / matrix[row, pivot_column], 4) == round(min_row, 4):
                                check = art_vert_header[row]
                                if check.startswith('A') or check.startswith('*'):
                                    min_row = matrix[row, numcolumns - 1] / matrix[row, pivot_column]
                                    pivot_row = row
                            else:
                                min_row = matrix[row, numcolumns - 1] / matrix[row, pivot_column]
                                pivot_row = row
        # Pivot row divided to convert into 1
        matrix[pivot_row, :] *= 1 / matrix[pivot_row, pivot_column]
        # We convert all numbers to 0 above and below
        for row in range(numrest+1):
            multiplier = matrix[row, pivot_column] * -1
            for column in range(numcolumns):
                if row != pivot_row:
                    if round(multiplier, 4) != 0:
                        matrix[row, column] += multiplier * matrix[pivot_row, column]
        # Change vertical header to variable that enter
        art_vert_header[pivot_row] = art_hor_header[pivot_column]

    def alternate_options(self, button):
        if button.text() == "Última iteración":
            if self.one_iteration.isChecked():
                self.all_iterations.setChecked(False)
            else:
                self.all_iterations.setChecked(True)
        else:
            if button.text() == "Todas las iteraciones":
                if self.all_iterations.isChecked():
                    self.one_iteration.setChecked(False)
                else:
                    self.one_iteration.setChecked(True)

    @staticmethod
    def has_infinite_solutions():
        global matrix
        infinite = False
        for column in range(numvar):
            if round(matrix[0, column], 4) == 0:
                for var in range(numrest+1):
                    if art_hor_header[column] == art_vert_header[var]:
                        break
                    else:
                        if var == numrest:
                            infinite = True
                            return infinite
        return infinite

    def optimal_solution(self):
        self.message.setIcon(QMessageBox.Information)
        self.message.setText(self.create_solution_string())
        self.message.setWindowTitle('Finalización')
        self.message.exec()
        self.iteration_lbl.setText("El problema tiene solución óptima")
        self.button_next.setEnabled(False)
        self.iteration_lbl.adjustSize()

    def infinite_solutions(self):
        self.message.setIcon(QMessageBox.Information)
        self.message.setText("El problema tiene infinitas soluciones")
        self.message.setWindowTitle('Finalización')
        self.message.exec()
        self.iteration_lbl.setText("El problema tiene infinitas soluciones")
        self.button_next.setEnabled(False)
        self.iteration_lbl.adjustSize()

    def unbounded_solution(self):
        self.message.setIcon(QMessageBox.Information)
        self.message.setText("El problema no está acotado")
        self.message.setWindowTitle('Finalización')
        self.message.exec()
        self.button_next.setEnabled(False)
        self.iteration_lbl.setText("El problema no está acotado")
        self.iteration_lbl.adjustSize()

    def no_solution(self):
        self.message.setIcon(QMessageBox.Information)
        self.message.setText("El problema no tiene solución")
        self.message.setWindowTitle('Finalización')
        self.message.exec()
        self.button_next.setEnabled(False)
        self.iteration_lbl.setText("El problema no tiene solución")
        self.iteration_lbl.adjustSize()

    @pyqtSlot()
    def call_window(self):
        no_deg = False
        for row in range(1, numrest + 1):
            if matrix[row, numcolumns - 1] > 0:
                no_deg = True
                break
        if no_deg:
            dialog = SensitivityAnalysis(self)
        else:
            self.message.setIcon(QMessageBox.Information)
            self.message.setText("El problema tiene solución degenerada por "
                                 "lo tanto no se puede ver el análisis de sensibilidad.")
            self.message.setWindowTitle('No dispobible')
            self.message.exec()

    @pyqtSlot()
    def reset_all(self):
        global status, numvar, numrest, current_iteration, phase1_done, matrix, arrayobj, arrayart, art_hor_header, \
            art_vert_header, signslist, rhs, variables, objfun, hasartvar, numcolumns, min_done
        self.vartext.setText('')
        self.resttext.setText('')
        status = 0
        numvar = 0
        numrest = 0
        current_iteration = 0
        phase1_done = False
        arrayart.clear()
        art_hor_header.clear()
        art_vert_header.clear()
        signslist.clear()
        rhs.clear()
        variables.clear()
        objfun = ""
        hasartvar = False
        numcolumns = 0
        min_done = False
        self.vartext.setEnabled(True)
        self.resttext.setEnabled(True)
        self.objective.setEnabled(True)
        self.table.setEnabled(False)
        self.button_next.hide()
        self.button_results.setEnabled(True)
        self.button_results.hide()
        self.one_iteration.setEnabled(True)
        self.all_iterations.setEnabled(True)
        self.button_confirm.setEnabled(True)
        self.button_analysis.hide()
        self.table.setRowCount(0)
        self.objfunction.setRowCount(0)
        self.iteration_lbl.setText('Confirmar restricciones')
        self.button_next.setEnabled(True)
        self.firstime = True
        self.reset.hide()


class SensitivityAnalysis(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Análisis de sensibilidad")
        self.setGeometry(120, 80, 900, 700)
        self.setFixedSize(900, 700)
        # Labels for everything
        label_obj = QLabel(self)
        label_obj.setText("Cambios coeficientes función objetivo")
        label_obj.adjustSize()
        label_obj.move(50, 375)
        label_rhs = QLabel(self)
        label_rhs.setText("Cambios lado derecho restricciones")
        label_rhs.adjustSize()
        label_rhs.move(50, 540)
        labelnum_it = QLabel(self)
        labelnum_it.setText("Número de iteraciones: "+str(current_iteration))
        labelnum_it.adjustSize()
        labelnum_it.move(50, 25)
        label_solution = QLabel(self)
        if objfun == "Max Z":
            label_solution.setText("Solución función objetivo: " + str(round(matrix[0, numcolumns - 1], 4)))
        else:
            label_solution.setText("Solución función objetivo: " + str(round(matrix[0, numcolumns - 1], 4) * -1))
        label_solution.adjustSize()
        label_solution.move(50, 50)
        # Setting up tables
        self.normal_values = QTableWidget(self)
        self.normal_values.setMaximumHeight(140)
        self.normal_values.setMinimumHeight(140)
        self.normal_values.setMaximumWidth(750)
        self.normal_values.setMinimumWidth(750)
        self.normal_values.setRowCount(numvar)
        self.normal_values.setColumnCount(4)
        self.normal_values.move(50, 75)
        # Tables change objective function
        self.change_coeff_obj = QTableWidget(self)
        self.change_coeff_obj.setMaximumHeight(140)
        self.change_coeff_obj.setMinimumHeight(140)
        self.change_coeff_obj.setMaximumWidth(750)
        self.change_coeff_obj.setMinimumWidth(750)
        self.change_coeff_obj.setRowCount(numvar)
        self.change_coeff_obj.setColumnCount(5)
        self.change_coeff_obj.move(50, 395)
        # Tables RHS normal
        self.normal_rhs = QTableWidget(self)
        self.normal_rhs.setMaximumHeight(140)
        self.normal_rhs.setMinimumHeight(140)
        self.normal_rhs.setMaximumWidth(750)
        self.normal_rhs.setMinimumWidth(750)
        self.normal_rhs.setRowCount(numrest)
        self.normal_rhs.setColumnCount(3)
        self.normal_rhs.move(50, 225)
        # Tables change RHS
        self.rhs_change = QTableWidget(self)
        self.rhs_change.setMaximumHeight(140)
        self.rhs_change.setMinimumHeight(140)
        self.rhs_change.setMaximumWidth(750)
        self.rhs_change.setMinimumWidth(750)
        self.rhs_change.setRowCount(numrest)
        self.rhs_change.setColumnCount(5)
        self.rhs_change.move(50, 555)
        self.init_table_normal()
        self.init_table_change_obj()
        self.init_table_rhs()
        self.init_table_change_rhs()
        self.show()

    def init_table_normal(self):
        normal_header = ["Variable", "Valor", "Obj Coeff", "Obj Val Contrib"]
        self.normal_values.setHorizontalHeaderLabels(normal_header)
        stylesheet = "::section{Background-color:rgb(0,255,255);border-radius:14px;}"
        self.normal_values.horizontalHeader().setStyleSheet(stylesheet)
        mlt = []
        for x in range(numvar):
            item = QTableWidgetItem()
            item.setText("X" + str(x + 1))
            self.normal_values.setItem(x, 0, item)
        for var in range(numvar):
            for r in range(numrest + 1):
                if art_vert_header[r] == self.normal_values.item(var, 0).text():
                    item2 = QTableWidgetItem()
                    item2.setText(str(round(matrix[r, numcolumns - 1], 4)))
                    mlt.append(matrix[r, numcolumns - 1])
                    self.normal_values.setItem(var, 1, item2)
                    break
                else:
                    if r == numrest:
                        item_zero = QTableWidgetItem()
                        item_zero.setText(str(0.0))
                        mlt.append(0)
                        self.normal_values.setItem(var, 1, item_zero)
        for x in range(numvar):
            item3 = QTableWidgetItem()
            item3.setText(str(round(arrayobj[0, x], 4)))
            self.normal_values.setItem(x, 2, item3)
            item4 = QTableWidgetItem()
            item4.setText(str(round(mlt[x] * arrayobj[0, x], 4)))
            self.normal_values.setItem(x, 3, item4)

    def init_table_change_obj(self):
        header = ["Variable", "Coeficiente Actual", "Min Coeff", "Max Coeff", "Costo reducido"]
        self.change_coeff_obj.setHorizontalHeaderLabels(header)
        stylesheet = "::section{Background-color:rgb(0,255,255);border-radius:14px;}"
        self.change_coeff_obj.horizontalHeader().setStyleSheet(stylesheet)
        min_array = []
        row_check = 0
        for c in range(numcolumns):
            if objfun == "Min Z":
                min_array.append(matrix[0, c] * -1)
            else:
                min_array.append(matrix[0, c])
        for x in range(numvar):
            item = QTableWidgetItem()
            item.setText("X" + str(x + 1))
            self.change_coeff_obj.setItem(x, 0, item)
        for x in range(numvar):
            item2 = QTableWidgetItem()
            item2.setText(str(round(arrayobj[0, x], 4)))
            self.change_coeff_obj.setItem(x, 1, item2)
        for x in range(numvar):
            if round(matrix[0, x], 4) != 0:
                item3 = QTableWidgetItem()
                item3.setText(str(round(matrix[0, x], 4)))
                if objfun == "Min Z":
                    item3.setText(str(round(matrix[0, x], 4) * -1))
                self.change_coeff_obj.setItem(x, 4, item3)
            else:
                item_zero = QTableWidgetItem()
                item_zero.setText(str(0.0))
                self.change_coeff_obj.setItem(x, 4, item_zero)
        for x in range(numvar):
            if round(min_array[x], 4) == 0:
                max_coef = 0
                min_coef = 0
                for y in range(numrest + 1):
                    if art_hor_header[x] == art_vert_header[y]:
                        row_check = y
                        break
                for col in range(numcolumns - 1):
                    check = art_hor_header[col]
                    if round(min_array[col], 4) != 0 and round(matrix[row_check, col], 4) != 0 and \
                            not check.startswith('*'):
                        if col >= numvar:
                            if signslist[col - numvar] == "=":
                                continue
                        aux = min_array[col] / matrix[row_check, col]
                        if 0 < round(aux, 4):
                            if min_coef == 0:
                                min_coef = round(aux, 4)
                            else:
                                if round(aux, 4) < min_coef:
                                    min_coef = round(aux, 4)
                        if round(aux, 4) < 0:
                            if max_coef == 0:
                                max_coef = abs(round(aux, 4))
                            else:
                                if abs(round(aux, 4)) < max_coef:
                                    max_coef = abs(round(aux, 4))
                item_max1 = QTableWidgetItem()
                item_min1 = QTableWidgetItem()
                if max_coef == 0:
                    item_max1.setText('infinity')
                    self.change_coeff_obj.setItem(x, 3, item_max1)
                    item_min1.setText(str(round(arrayobj[0, x] - min_coef, 4)))
                    self.change_coeff_obj.setItem(x, 2, item_min1)
                else:
                    if min_coef == 0:
                        item_max1.setText('-infinity')
                        self.change_coeff_obj.setItem(x, 2, item_max1)
                        item_min1.setText(str(round(arrayobj[0, x] + max_coef, 4)))
                        self.change_coeff_obj.setItem(x, 3, item_min1)
                    else:
                        item_max1.setText(str(round(arrayobj[0, x] + max_coef, 4)))
                        self.change_coeff_obj.setItem(x, 3, item_max1)
                        item_min1.setText(str(round(arrayobj[0, x] - min_coef, 4)))
                        self.change_coeff_obj.setItem(x, 2, item_min1)
            else:
                if round(min_array[x], 4) < 0:
                    item_min = QTableWidgetItem()
                    item_min.setText(str(round(arrayobj[0, x] - matrix[0, x], 4)))
                    self.change_coeff_obj.setItem(x, 2, item_min)
                    item_inf = QTableWidgetItem()
                    item_inf.setText(str('infinity'))
                    self.change_coeff_obj.setItem(x, 3, item_inf)
                else:
                    item_max = QTableWidgetItem()
                    item_max.setText(str(round(arrayobj[0, x] + matrix[0, x], 4)))
                    self.change_coeff_obj.setItem(x, 3, item_max)
                    item_inf2 = QTableWidgetItem()
                    item_inf2.setText(str('-infinity'))
                    self.change_coeff_obj.setItem(x, 2, item_inf2)

    def init_table_rhs(self):
        header = ["Desigualdad", "RHS", "Slack(-)/Surplus(+)"]
        self.normal_rhs.setHorizontalHeaderLabels(header)
        stylesheet = "::section{Background-color:rgb(0,255,255);border-radius:14px;}"
        self.normal_rhs.horizontalHeader().setStyleSheet(stylesheet)
        for x in range(numrest):
            item = QTableWidgetItem()
            item.setText(signslist[x])
            self.normal_rhs.setItem(x, 0, item)
            item2 = QTableWidgetItem()
            item2.setText(str(rhs[x]))
            self.normal_rhs.setItem(x, 1, item2)
        for y in range(numrest):
            check = variables[y]
            if check.startswith('E') or check.startswith('H'):
                for row in range(numrest + 1):
                    if check == art_vert_header[row]:
                        item3 = QTableWidgetItem()
                        if check.startswith('E'):
                            aux = str(round(matrix[row, numcolumns - 1], 4))
                            aux += str('+')
                            item3.setText(aux)
                        else:
                            aux = str(round(matrix[row, numcolumns - 1], 4))
                            aux += str('-')
                            item3.setText(aux)
                        self.normal_rhs.setItem(y, 2, item3)
                        break
                    else:
                        if row == numrest:
                            item_zero = QTableWidgetItem()
                            item_zero.setText(str(0.0))
                            self.normal_rhs.setItem(y, 2, item_zero)
            else:
                item_zero2 = QTableWidgetItem()
                item_zero2.setText(str(0.0))
                self.normal_rhs.setItem(y, 2, item_zero2)

    def init_table_change_rhs(self):
        header = ["Desigualdad", "RHS actual", "Min RHS", "Max RHS", "Precio dual"]
        self.rhs_change.setHorizontalHeaderLabels(header)
        stylesheet = "::section{Background-color:rgb(0,255,255);border-radius:14px;}"
        self.rhs_change.horizontalHeader().setStyleSheet(stylesheet)
        for x in range(numrest):
            item = QTableWidgetItem()
            item.setText(signslist[x])
            self.rhs_change.setItem(x, 0, item)
            item2 = QTableWidgetItem()
            item2.setText(str(rhs[x]))
            self.rhs_change.setItem(x, 1, item2)
            if objfun == "Max Z":
                if signslist[x] == '>=':
                    self.rhs_change.setItem(x, 4, QTableWidgetItem(str(round(matrix[0, x + numvar] * -1, 4))))
                else:
                    self.rhs_change.setItem(x, 4, QTableWidgetItem(str(round(matrix[0, x + numvar], 4))))
            else:
                if signslist[x] == '>=':
                    self.rhs_change.setItem(x, 4, QTableWidgetItem(str(round(matrix[0, x + numvar], 4))))
                else:
                    self.rhs_change.setItem(x, 4, QTableWidgetItem(str(round(matrix[0, x + numvar] * -1, 4))))
        for rest in range(numrest):
            max_rhs = 0
            min_rhs = 0
            all_same = False
            mult = 1
            if signslist[rest] == '<=' or signslist[rest] == "=":
                mult *= -1
            for row in range(1, numrest + 1):
                if round(matrix[row, rest + numvar], 4) != 0:
                    result = matrix[row, numcolumns - 1] / (matrix[row, rest + numvar] * mult)
                    if round(result, 4) > 0:
                        if max_rhs == 0:
                            max_rhs = result
                        else:
                            if round(result, 4) < round(max_rhs, 4):
                                max_rhs = result
                    else:
                        if min_rhs == 0:
                            min_rhs = abs(result)
                        else:
                            if abs(round(result, 4)) < round(min_rhs, 4):
                                min_rhs = abs(result)
            if min_rhs != 0 and max_rhs != 0:
                self.rhs_change.setItem(rest, 2, QTableWidgetItem(str(round(rhs[rest] - min_rhs, 4))))
                self.rhs_change.setItem(rest, 3, QTableWidgetItem(str(round(rhs[rest] + max_rhs, 4))))
            else:
                if min_rhs == 0 and max_rhs == 0:
                    self.rhs_change.setItem(rest, 2, QTableWidgetItem('-infinity'))
                    self.rhs_change.setItem(rest, 3, QTableWidgetItem('infinity'))
                else:
                    if max_rhs == 0:
                        if self.check_all_same(rest, mult):
                            self.rhs_change.setItem(rest, 2, QTableWidgetItem('-infinity'))
                            self.rhs_change.setItem(rest, 3, QTableWidgetItem('infinity'))
                        else:
                            self.rhs_change.setItem(rest, 2, QTableWidgetItem(str(round(rhs[rest] - min_rhs, 4))))
                            self.rhs_change.setItem(rest, 3, QTableWidgetItem('infinity'))
                    else:
                        if self.check_all_same(rest, mult):
                            self.rhs_change.setItem(rest, 2, QTableWidgetItem('-infinity'))
                            self.rhs_change.setItem(rest, 3, QTableWidgetItem('infinity'))
                        else:
                            self.rhs_change.setItem(rest, 2, QTableWidgetItem('-infinity'))
                            self.rhs_change.setItem(rest, 3, QTableWidgetItem(str(round(rhs[rest] + max_rhs, 4))))

    @staticmethod
    def check_all_same(column, mult):
        result = 0
        check = 0
        for row in range(1, numrest + 1):
            if round(matrix[row, column + numvar], 4) != 0:
                if row == 1:
                    check = matrix[row, numcolumns - 1] / (matrix[row, column + numvar] * mult)
                result += matrix[row, numcolumns - 1] / (matrix[row, column + numvar] * mult)
            else:
                return False
        if abs(round(result / (numrest * check), 4)) == 1:
            return True
        else:
            return False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    simp = SimplexWindow()
    sys.exit(app.exec())