import sys
import numpy as np
import matplotlib
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QComboBox, QMessageBox
)

class CampoVectorialApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Campo Vectorial 2D / 3D")
        self.resize(900, 700)

        # Layout principal
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self._crear_panel_superior()
        self._crear_canvas()
        self._aplicar_estilo()

    # --------------------------------------------------
    # Panel superior (entradas + selector + botón principal)
    # --------------------------------------------------
    def _crear_panel_superior(self):
        fila1 = QHBoxLayout()
        self.inputU = QLineEdit(); self.inputU.setPlaceholderText("U(x, y[, z])")
        self.inputV = QLineEdit(); self.inputV.setPlaceholderText("V(x, y[, z])")
        self.inputW = QLineEdit(); self.inputW.setPlaceholderText("W(x, y, z) - opcional")
        self.selector = QComboBox(); self.selector.addItems(["2D", "3D"])
        fila1.addWidget(self.inputU)
        fila1.addWidget(self.inputV)
        fila1.addWidget(self.inputW)
        fila1.addWidget(self.selector)
        self.layout.addLayout(fila1)

        self.boton = QPushButton("Graficar Campo")
        self.boton.clicked.connect(self.graficar)
        self.layout.addWidget(self.boton)

    # --------------------------------------------------
    # Canvas Matplotlib
    # --------------------------------------------------
    def _crear_canvas(self):
        self.fig = plt.figure(figsize=(7, 6))
        self.canvas = FigureCanvas(self.fig)
        self.layout.addWidget(self.canvas)

    # --------------------------------------------------
    # Estilo fijo modo claro
    # --------------------------------------------------
    def _aplicar_estilo(self):
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                color: black;
                font-size: 13px;
            }
            QLineEdit {
                background-color: #f0f0f0;
                color: black;
                border-radius: 5px;
                padding: 6px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 8px;
            }
            QComboBox {
                background-color: #e0e0e0;
                color: black;
                border-radius: 5px;
                padding: 5px;
            }
        """)

    # --------------------------------------------------
    # Graficar campo
    # --------------------------------------------------
    def graficar(self):
        modo = self.selector.currentText()
        U_expr, V_expr, W_expr = self.inputU.text(), self.inputV.text(), self.inputW.text()

        try:
            self.fig.clear()
            if modo == "2D":
                self.graficar_2D(U_expr, V_expr)
            else:
                self.graficar_3D(U_expr, V_expr, W_expr or "0")
            self.canvas.draw()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error:\n{e}")

    # --------------------------------------------------
    # Graficar 2D
    # --------------------------------------------------
    def graficar_2D(self, expr_U, expr_V):
        ax = self.fig.add_subplot(111)
        x, y = np.linspace(-5, 5, 20), np.linspace(-5, 5, 20)
        X, Y = np.meshgrid(x, y)

        U = eval(expr_U, {"np": np, "x": X, "y": Y})
        V = eval(expr_V, {"np": np, "x": X, "y": Y})
        M = np.sqrt(U**2 + V**2)
        M[M == 0] = 1e-9

        cmap = plt.cm.plasma
        norm = matplotlib.colors.Normalize(vmin=M.min(), vmax=M.max())

        ax.set_facecolor("white")
        q = ax.quiver(X, Y, U, V, M, cmap=cmap, norm=norm,
                      scale=25, width=0.007,
                      headwidth=2, headlength=3, headaxislength=2.5)

        ax.set_title("Campo Vectorial 2D", color="black", pad=10)
        ax.set_xlabel("x", color="black")
        ax.set_ylabel("y", color="black")
        ax.tick_params(colors="black")
        ax.set_aspect("equal")
        ax.grid(True, color="#cccccc")

        for cbar in self.fig.axes:
            if hasattr(cbar, 'get_label'):
                try:
                    if "Magnitud" in cbar.get_ylabel():
                        cbar.remove()
                except:
                    pass

        cbar = self.fig.colorbar(q, ax=ax, shrink=0.8, aspect=10, pad=0.05)
        cbar.set_label("Magnitud", color="black")
        cbar.ax.yaxis.set_tick_params(color="black")
        plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color="black")

        self.fig.subplots_adjust(left=0.01, right=0.8, top=0.93, bottom=0.08)

    # --------------------------------------------------
    # Graficar 3D
    # --------------------------------------------------
    def graficar_3D(self, expr_U, expr_V, expr_W):
        ax = self.fig.add_subplot(111, projection="3d")
        x = np.linspace(-3, 3, 8)
        y = np.linspace(-3, 3, 8)
        z = np.linspace(-3, 3, 8)
        X, Y, Z = np.meshgrid(x, y, z)
        U = eval(expr_U, {"np": np, "x": X, "y": Y, "z": Z})
        V = eval(expr_V, {"np": np, "x": X, "y": Y, "z": Z})
        W = eval(expr_W, {"np": np, "x": X, "y": Y, "z": Z})

        M = np.sqrt(U**2 + V**2 + W**2)
        M[M == 0] = 1e-9

        cmap = plt.cm.plasma
        norm = matplotlib.colors.Normalize(vmin=M.min(), vmax=M.max())
        colors = cmap(norm(M))

        ax.quiver(X, Y, Z, U, V, W, length=0.6,
                  arrow_length_ratio=0.35, normalize=True,
                  linewidth=1.3, colors=colors.reshape(-1, 4))

        ax.set_facecolor("white")
        self.fig.patch.set_facecolor("white")
        ax.set_title("Campo Vectorial 3D", color="black")
        ax.set_xlabel("x", color="black")
        ax.set_ylabel("y", color="black")
        ax.set_zlabel("z", color="black")
        ax.tick_params(colors="black")
        ax.grid(True, color="#cccccc")

        for cbar in self.fig.axes:
            if hasattr(cbar, 'get_label'):
                try:
                    if "Magnitud" in cbar.get_ylabel():
                        cbar.remove()
                except:
                    pass

        mappable = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
        mappable.set_array(M)
        cbar = self.fig.colorbar(mappable, ax=ax, shrink=0.6, aspect=12, pad=0.08)
        cbar.set_label("Magnitud", color="black")
        plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color="black")

        self.fig.tight_layout()
        self.fig.subplots_adjust(left=0.07, right=0.9)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = CampoVectorialApp()
    ventana.show()
    sys.exit(app.exec())


