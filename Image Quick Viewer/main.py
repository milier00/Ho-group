import sys
sys.path.append("./resource/")
sys.path.append("./model/")
sys.path.append("./ui/")
from QuickView import myQuickViewWindow
from PyQt5.QtWidgets import QApplication


if __name__ == "__main__":
    # create the application and the main window
    app = QApplication(sys.argv)
    window = myQuickViewWindow()
    app.setStyle("Fusion")
    window.show()
    sys.exit(app.exec_())