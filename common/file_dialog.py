from PyQt5.QtWidgets import QFileDialog


class App(QFileDialog):

    def __init__(self, dialog_type):
        super().__init__()

        self.fileName = ""
        self.model_file_path = ""
        self.initUI(dialog_type)

    def initUI(self, dialog_type):
        if dialog_type == "INPUTFILE":
            self.openFileNameDialog()
        elif dialog_type == "EMGAATSGDB":
            self.open_emgaats_gdb()

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        self.fileName, _ = QFileDialog.getOpenFileName(self, "Select HSPF Utility input file", "",
                                                  "Excel Files (*.xlsx)", options=options)

    def open_emgaats_gdb(self):
        self.setFileMode(QFileDialog.Directory)
        self.model_file_path = QFileDialog.getExistingDirectory(self, "Select EmgaatsModel.gdb to check")