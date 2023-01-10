import sys
sys.path.append('./ui/')
sys.path.append('./model/')
sys.path.append("./Plot2D3D/")
from SpcProcessing import mySpcProcessing
from PyQt5.QtWidgets import QApplication



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = mySpcProcessing()
    window.show()
    sys.exit(app.exec_())