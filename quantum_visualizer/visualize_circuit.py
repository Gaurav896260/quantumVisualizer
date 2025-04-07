from qiskit import QuantumCircuit
import matplotlib.pyplot as plt

def draw_circuit():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()
    
    qc.draw('mpl')
    plt.show()

if __name__ == "__main__":
    draw_circuit()


