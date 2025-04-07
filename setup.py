from setuptools import setup, find_packages

setup(
    name="quantum_visualizer",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "matplotlib",
        "qiskit",
        "pyqt6",
        "pylatexenc"
    ],
    entry_points={
        'console_scripts': [
            'quantum-visualizer=quantum_visualizer.main:run'
        ],
    },
)
