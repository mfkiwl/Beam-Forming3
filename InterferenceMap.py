

import numpy as np
from PyQt5.QtWidgets import *

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class FieldPlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.color = np.random.rand(3,)
        
    def setup_ui(self):
        layout = QVBoxLayout()
        self.figure = Figure(figsize=(12, 8))
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.ax_field = self.figure.add_subplot(111)
        self.figure.tight_layout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
    def update_plot(self, arrays):
        self.ax_field.clear()
        
        # Field plot
        x = np.linspace(-5, 5, 50)
        y = np.linspace(0, 6, 50)
        X, Y = np.meshgrid(x, y)
        Z = np.zeros_like(X, dtype=complex)
        
        for array in arrays:
            for element in array.elements:
                points = np.stack([X.flatten(), Y.flatten()], axis=1)
                field = np.array([element.calculate_field(point) for point in points])
                Z += field.reshape(X.shape)
                
        self.ax_field.contourf(X, Y, np.abs(Z), levels=50)
        self.ax_field.set_title('Field Intensity')
        self.ax_field.set_aspect('equal')
        self.figure.tight_layout()
        self.canvas.draw()
        # self.plot_target_point(3,3)

    def plot_target_point(self,x,y):
        self.ax_field.plot(x, y, 'ro', color=self.color)
        self.canvas.draw()