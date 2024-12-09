import json
import sys
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QTimer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from Array import Array
from mainwin import Ui_MainWindow
from InterferenceMap import FieldPlotWidget
from BeamPattern import PolarPlotWidget
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setup_plots()
        self.setup_controls()
        self.block = False
        self.arrays = []
        # self.timer = QTimer()
        # self.timer.timeout.connect(self.update_simulation)
        # self.timer.start(100)

    def setup_plots(self):
        self.field_plot = FieldPlotWidget()
        beam_layout = QVBoxLayout(self.ui.beamPatternTab)
        beam_layout.addWidget(self.field_plot)

        self.polar_plot = PolarPlotWidget()
        interference_layout = QVBoxLayout(self.ui.interferenceMapTab)
        interference_layout.addWidget(self.polar_plot)

    def setup_controls(self):
        self.ui.addArrayButton.clicked.connect(self.add_array)
        self.ui.removeArrayButton.clicked.connect(self.remove_array)
        self.ui.arrayList.currentRowChanged.connect(lambda index: self.on_array_selected(index))

        self.ui.xPosition.valueChanged.connect(self.update_selected_array)
        self.ui.yPosition.valueChanged.connect(self.update_selected_array)
        self.ui.rotation.valueChanged.connect(self.update_selected_array)
        self.ui.numElements.valueChanged.connect(self.update_selected_array)
        self.ui.elementSpacing.valueChanged.connect(self.update_selected_array)
        self.ui.curvature.valueChanged.connect(self.update_selected_array)
        self.ui.steeringAngle.valueChanged.connect(self.update_selected_array)

        self.ui.addFrequencyButton.clicked.connect(self.add_frequency)
        self.ui.removeFrequencyButton.clicked.connect(self.remove_frequency)

        self.ui.comboBox_2.addItems(['Hz', 'kHz', 'MHz'])

        self.ui.saveScenarioButton.clicked.connect(self.save_scenario)
        self.ui.loadScenarioButton.clicked.connect(self.load_scenario_from_device)

        self.ui.scenarioSelect.currentIndexChanged.connect(self.load_selected_scenario)
        self.populate_scenario_select()

    def save_scenario(self):
        try:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Scenario", "scenarios/",
                                                       "JSON Files (*.json);;All Files (*)", options=options)
            if file_name:
                scenario = {
                    "arrays": [
                        {
                            "center": array.center.tolist(),
                            "num_elements": array.num_elements,
                            "radius": array.radius,
                            "curvature": array.curvature,
                            "rotation": array.rotation,
                            "steering_angle": array.steering_angle,
                            "frequencies": [element.frequencies for element in array.elements]
                        }
                        for array in self.arrays
                    ]
                }
                with open(file_name, 'w') as file:
                    json.dump(scenario, file, indent=4)
                print("Scenario saved successfully.")
                self.populate_scenario_select()
        except Exception as e:
            print(f"An error occurred while saving the scenario: {e}")

    def load_scenario_from_device(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Scenario", "", "JSON Files (*.json);;All Files (*)",
                                                   options=options)
        if file_name:
            with open(file_name, 'r') as file:
                scenario = json.load(file)
                self.arrays.clear()
                self.ui.arrayList.clear()
                for array_data in scenario["arrays"]:
                    array = Array(
                        center=array_data["center"],
                        num_elements=array_data["num_elements"],
                        radius=array_data["radius"],
                        curvature=array_data["curvature"],
                        rotation=array_data["rotation"]
                    )
                    array.set_steering_angle(array_data["steering_angle"])
                    for element, freqs in zip(array.elements, array_data["frequencies"]):
                        element.frequencies = freqs
                    self.arrays.append(array)
                    self.ui.arrayList.addItem(f"Array {len(self.arrays)}")
                if self.arrays:
                    self.ui.arrayList.setCurrentRow(0)
                self.update_simulation()

    def load_selected_scenario(self, index):
        file_name = self.ui.scenarioSelect.currentText()
        if file_name:
            file_path = os.path.join("scenarios", file_name)
            with open(file_path, 'r') as file:
                scenario = json.load(file)
                self.arrays.clear()
                self.ui.arrayList.clear()
                for array_data in scenario["arrays"]:
                    array = Array(
                        center=array_data["center"],
                        num_elements=array_data["num_elements"],
                        radius=array_data["radius"],
                        curvature=array_data["curvature"],
                        rotation=array_data["rotation"]
                    )
                    array.set_steering_angle(array_data["steering_angle"])
                    for element, freqs in zip(array.elements, array_data["frequencies"]):
                        element.frequencies = freqs
                    self.arrays.append(array)
                    self.ui.arrayList.addItem(f"Array {len(self.arrays)}")
                if self.arrays:
                    self.ui.arrayList.setCurrentRow(0)
                self.update_simulation()

    def populate_scenario_select(self):
        current_selection = self.ui.scenarioSelect.currentText()
        self.ui.scenarioSelect.blockSignals(True)
        self.ui.scenarioSelect.clear()
        scenario_dir = "scenarios"  # Directory where scenarios are saved
        if not os.path.exists(scenario_dir):
            os.makedirs(scenario_dir)
        for file_name in os.listdir(scenario_dir):
            if file_name.endswith(".json"):
                self.ui.scenarioSelect.addItem(file_name)
        if current_selection:
            index = self.ui.scenarioSelect.findText(current_selection)
            if index != -1:
                self.ui.scenarioSelect.setCurrentIndex(index)
        self.ui.scenarioSelect.blockSignals(False)

    def add_array(self):
        array = Array()
        self.arrays.append(array)
        self.ui.arrayList.addItem(f"Array {len(self.arrays)}")
        if len(self.arrays) == 1:
            self.ui.arrayList.setCurrentRow(0)
        self.update_simulation()

    def remove_array(self):
        current_row = self.ui.arrayList.currentRow()
        if current_row >= 0:
            self.arrays.pop(current_row)
            self.ui.arrayList.takeItem(current_row)
            self.update_simulation()

    def on_array_selected(self, index):
        self.block = True
        if index >= 0 and index < len(self.arrays):
            # print(index)
            array = self.arrays[index]
            self.ui.steeringAngle.setValue(array.steering_angle)
            self.ui.numElements.setValue(array.num_elements)
            self.ui.elementSpacing.setValue(array.radius / max(1, array.num_elements - 1))
            self.ui.curvature.setValue(array.curvature)
            self.ui.xPosition.setValue(array.center[0])
            self.ui.yPosition.setValue(array.center[1])
            self.ui.rotation.setValue(int(array.rotation))
        self.block = False


    def add_frequency(self):
        freq = self.ui.frequencyInput.value()
        unit = self.ui.comboBox_2.currentText()
        if unit == 'kHz':
            freq *= 1000
        elif unit == 'MHz':
            freq *= 1000000
        self.ui.frequencyList.addItem(f"{freq} Hz")

    def remove_frequency(self):
        current_row = self.ui.frequencyList.currentRow()
        if current_row >= 0:
            self.ui.frequencyList.takeItem(current_row)

    def update_selected_array(self):
        if self.block:
            return
        current_row = self.ui.arrayList.currentRow()
        if current_row >= 0 and current_row < len(self.arrays):
            array = self.arrays[current_row]
            array.num_elements = self.ui.numElements.value()
            array.radius = self.ui.elementSpacing.value() * (array.num_elements - 1)
            array.curvature = self.ui.curvature.value()
            
            array.center = np.array([self.ui.xPosition.value(), self.ui.yPosition.value()])
            array.rotation = self.ui.rotation.value()
            
            array.create_array()
            array.set_steering_angle(self.ui.steeringAngle.value())

            freqs = []
            for i in range(self.ui.frequencyList.count()):
                freq_text = self.ui.frequencyList.item(i).text()
                freq = float(freq_text.split()[0])
                freqs.append(freq)
            
            if freqs:
                for element in array.elements:
                    element.frequencies = freqs
            self.update_simulation()

    def update_simulation(self):
        self.field_plot.update_plot(self.arrays)
        self.polar_plot.update_plot(self.arrays)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())