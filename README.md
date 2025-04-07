# Quantum Visualizer

A Python-based GUI tool for visualizing quantum circuits and Bloch spheres using Qiskit and PyQt6.  
This tool lets users interactively explore quantum mechanics concepts — perfect for learners, educators, and developers.

---

## 📦 Project Structure

quantum_visualizer/
├── build/ -> Build artifacts
│ └── bdist.win-amd64/ -> Platform-specific build directory
├── dist/ -> Distributable packages (wheel, tar.gz)
│ ├── quantum_visualizer-0.1-py3-none-any.whl
│ └── quantum_visualizer-0.1.tar.gz
├── quantum_visualizer/ -> Main source code
│ ├── **pycache**/ -> Compiled Python cache
│ │ ├── bloch_visualizer.cpython-312.pyc
│ │ └── visualize_circuit.cpython-312.pyc
│ ├── bloch_visualizer.py -> Code to visualize Bloch Sphere
│ ├── visualize_circuit.py -> Code to draw and show quantum circuits
│ └── main.py -> PyQt6-based GUI for visual interaction
├── quantum_visualizer.egg-info/ -> Packaging metadata
│ ├── dependency_links.txt
│ ├── entry_points.txt
│ ├── PKG-INFO
│ ├── requires.txt
│ ├── SOURCES.txt
│ └── top_level.txt
└── setup.py -> Packaging configuration script

---

## 🚀 How to Run

1. 📦 Install dependencies:
   pip install qiskit pyqt6 matplotlib pylatexenc

2. ▶️ Run the application:
   python quantum_visualizer/main.py

You’ll see a simple GUI window with buttons to:

- Visualize a sample quantum circuit
- Display the Bloch sphere for a single qubit state

---

## 🛠 Features

- Visualize quantum circuits using Qiskit + Matplotlib
- Generate Bloch spheres interactively
- Clean and minimal PyQt6 interface
- Easy to extend for other visualizations like measurement, superposition, entanglement

---

## 📦 Packaging & Distribution

To build the package locally:

```bash
python setup.py sdist bdist_wheel
```
