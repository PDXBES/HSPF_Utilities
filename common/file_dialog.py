from PyQt5.QtWidgets import QFileDialog


class App(QFileDialog):

    def __init__(self):
        super().__init__()

        self.fileName = ""
        self.initUI()

    def initUI(self):
        self.openFileNameDialog()

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        self.fileName, _ = QFileDialog.getOpenFileName(self, "Select HSPF Utility input file", "",
                                                  "Excel Files (*.xlsx)", options=options)