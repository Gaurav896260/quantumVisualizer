from qiskit.visualization import plot_bloch_vector
import matplotlib.pyplot as plt
import numpy as np

def bloch_sphere():
    bloch_vector = [1, 0, 0]  # X-axis
    plot_bloch_vector(bloch_vector)
    plt.show()

if __name__ == "__main__":
    bloch_sphere()
