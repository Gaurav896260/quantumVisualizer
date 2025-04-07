from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, 
    QLabel, QFrame, QHBoxLayout, QSplitter, QStackedWidget,
    QComboBox, QSlider, QSpinBox, QGroupBox, QGridLayout
)
from PyQt6.QtCore import Qt, QSize, pyqtSlot, QTimer
from PyQt6.QtGui import QFont, QIcon, QPixmap, QColor, QPalette, QLinearGradient, QGradient
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from mpl_toolkits.mplot3d import Axes3D
from bloch_visualizer import bloch_sphere  # Import from the correct file
from visualize_circuit import draw_circuit


class StyledButton(QPushButton):
    def __init__(self, text, icon_path=None):
        super().__init__(text)
        self.setMinimumHeight(50)
        self.setFont(QFont('Arial', 10, QFont.Weight.Bold))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: #2C3E50;
                color: white;
                border-radius: 6px;
                padding: 10px 15px;
            }
            QPushButton:hover {
                background-color: #34495E;
            }
            QPushButton:pressed {
                background-color: #1ABC9C;
            }
        """)
        
        if icon_path and os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(24, 24))


class MatplotlibCanvas(FigureCanvas):
    def __init__(self, width=8, height=6, dpi=100):
        self.fig = plt.figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setStyleSheet("background-color: transparent;")


class InfoPanel(QFrame):
    def __init__(self, title, description):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: #2C3E50;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        title_label = QLabel(title)
        title_label.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #1ABC9C;")
        
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #ECF0F1;")
        
        layout.addWidget(title_label)
        layout.addWidget(desc_label)


def visualize_quantum_states():
    """Function to visualize various quantum states"""
    # Create a new window for quantum states visualization
    state_window = QWidget()
    state_window.setWindowTitle("Quantum States Visualization")
    state_window.setGeometry(200, 200, 900, 700)
    state_window.setStyleSheet("background-color: #1A2930;")
    
    layout = QVBoxLayout()
    
    # Title
    title = QLabel("Quantum States Visualization")
    title.setFont(QFont('Arial', 16, QFont.Weight.Bold))
    title.setStyleSheet("color: #1ABC9C; margin-bottom: 20px;")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(title)
    
    # Add controls for interactive visualization
    controls_frame = QFrame()
    controls_frame.setStyleSheet("background-color: #253443; border-radius: 6px; padding: 10px;")
    controls_layout = QHBoxLayout(controls_frame)
    
    # State selection
    state_selector = QComboBox()
    state_selector.addItems(["|0⟩", "|1⟩", "|+⟩", "|-⟩", "|+i⟩", "|-i⟩"])
    state_selector.setStyleSheet("""
        QComboBox {
            background-color: #2C3E50;
            color: white;
            border-radius: 4px;
            padding: 5px;
            min-width: 100px;
        }
        QComboBox::drop-down {
            border-color: #34495E;
        }
        QComboBox QAbstractItemView {
            background-color: #2C3E50;
            color: white;
            selection-background-color: #1ABC9C;
        }
    """)
    
    # Add a spin parameter control
    phase_control = QSlider(Qt.Orientation.Horizontal)
    phase_control.setRange(0, 100)
    phase_control.setValue(0)
    phase_control.setStyleSheet("""
        QSlider::groove:horizontal {
            height: 8px;
            background: #34495E;
            border-radius: 4px;
        }
        QSlider::handle:horizontal {
            background: #1ABC9C;
            width: 16px;
            margin: -4px 0;
            border-radius: 8px;
        }
    """)
    
    # Labels
    state_label = QLabel("Select State:")
    state_label.setStyleSheet("color: white;")
    phase_label = QLabel("Phase (0-2π):")
    phase_label.setStyleSheet("color: white;")
    
    # Add widgets to controls
    controls_layout.addWidget(state_label)
    controls_layout.addWidget(state_selector)
    controls_layout.addSpacing(20)
    controls_layout.addWidget(phase_label)
    controls_layout.addWidget(phase_control)
    
    layout.addWidget(controls_frame)
    
    # Create matplotlib canvas for visualization
    canvas = MatplotlibCanvas(width=8, height=5)
    layout.addWidget(canvas)
    
    # Plot example quantum states
    ax = canvas.fig.add_subplot(111)
    
    # Define some common quantum states for visualization
    # |0>, |1>, |+>, |-> states probabilities in computational basis
    states = {
        "|0>": [1, 0],
        "|1>": [0, 1],
        "|+>": [0.5, 0.5],
        "|->": [0.5, 0.5],
        "|+i>": [0.5, 0.5],
        "|-i>": [0.5, 0.5]
    }
    
    # Phases for the states
    phases = {
        "|0>": [0, 0],
        "|1>": [0, 0],
        "|+>": [0, 0],
        "|->": [0, np.pi],
        "|+i>": [0, np.pi/2],
        "|-i>": [0, -np.pi/2]
    }
    
    def update_plot(state_idx=None):
        ax.clear()
        # If a state is selected from the dropdown
        if state_idx is not None:
            state_name = state_selector.currentText().replace("⟩", ">").replace("⟨", "<")
            
            # Get phase adjustment from slider (0 to 2π)
            phase_adj = phase_control.value() * (2 * np.pi / 100)
            
            # Apply phase adjustment to the selected state
            current_phases = phases[state_name].copy()
            current_phases = [p + phase_adj for p in current_phases]
            
            # For real part (based on phase)
            probs = states[state_name]
            reals = [prob * np.cos(phase) for prob, phase in zip(probs, current_phases)]
            # For imaginary part (based on phase)
            imags = [prob * np.sin(phase) for prob, phase in zip(probs, current_phases)]
            
            x_pos = np.array([0, 1])
            
            # Plot real parts
            ax.bar(x_pos, reals, 0.35, label=f"Real", alpha=0.7, color='#3498DB')
            
            # Plot imaginary parts with hatching
            ax.bar(x_pos + 0.35, imags, 0.35, label=f"Imag", alpha=0.7, color='#E74C3C', hatch='///')
            
            ax.set_title(f'Quantum State: {state_selector.currentText()}', color='white')
        else:
            # Plot multiple states for comparison
            x = np.arange(len(states))
            width = 0.2
            
            # Plot the probability amplitudes for each state
            for i, (state_name, probs) in enumerate(states.items()):
                # For real part (based on phase)
                reals = [prob * np.cos(phase) for prob, phase in zip(probs, phases[state_name])]
                # For imaginary part (based on phase)
                imags = [prob * np.sin(phase) for prob, phase in zip(probs, phases[state_name])]
                
                x_pos = np.array([0, 1]) + i * width * 2
                
                # Plot real parts
                ax.bar(x_pos, reals, width, label=f"{state_name} (Real)", alpha=0.7, 
                       color=plt.cm.viridis(i/len(states)))
                
                # Plot imaginary parts with hatching
                ax.bar(x_pos + width, imags, width, label=f"{state_name} (Imag)", alpha=0.7,
                       color=plt.cm.viridis(i/len(states)), hatch='///')
            
            ax.set_title('Quantum State Representations', color='white')
        
        ax.set_ylabel('Amplitude', color='white')
        ax.set_xticks([0.3, 1.3])
        ax.set_xticklabels(['|0⟩', '|1⟩'])
        ax.legend(loc='upper right')
        
        # Style the plot for dark mode
        ax.set_facecolor('#253443')
        canvas.fig.patch.set_facecolor('#1A2930')
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('white')
        
        canvas.draw()
    
    # Initial plot
    update_plot()
    
    # Connect controls to update function
    state_selector.currentIndexChanged.connect(update_plot)
    phase_control.valueChanged.connect(lambda: update_plot(state_selector.currentIndex()))
    
    # Description label
    description = QLabel(
        "This visualization shows the probability amplitudes of quantum states "
        "in the computational basis. The real and imaginary components are shown separately. "
        "You can select different states and adjust their phase to see how the representation changes."
    )
    description.setWordWrap(True)
    description.setStyleSheet("color: #ECF0F1; margin: 20px 0;")
    layout.addWidget(description)
    
    # Set the layout and show the window
    state_window.setLayout(layout)
    state_window.show()
    
    # Keep a reference to prevent garbage collection
    state_window.canvas = canvas
    state_window.controls = (state_selector, phase_control)  # Keep references
    
    return state_window


def visualize_entanglement():
    """Function to visualize quantum entanglement between two qubits"""
    # Create a new window for entanglement visualization
    ent_window = QWidget()
    ent_window.setWindowTitle("Quantum Entanglement Visualization")
    ent_window.setGeometry(200, 200, 900, 700)
    ent_window.setStyleSheet("background-color: #1A2930;")
    
    layout = QVBoxLayout()
    
    # Title
    title = QLabel("Quantum Entanglement Visualization")
    title.setFont(QFont('Arial', 16, QFont.Weight.Bold))
    title.setStyleSheet("color: #1ABC9C; margin-bottom: 20px;")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(title)
    
    # Add controls for bell state selection
    controls_frame = QFrame()
    controls_frame.setStyleSheet("background-color: #253443; border-radius: 6px; padding: 10px;")
    controls_layout = QHBoxLayout(controls_frame)
    
    # Bell state selection
    state_selector = QComboBox()
    state_selector.addItems(["Φ+ (|00⟩ + |11⟩)/√2", "Φ- (|00⟩ - |11⟩)/√2", 
                             "Ψ+ (|01⟩ + |10⟩)/√2", "Ψ- (|01⟩ - |10⟩)/√2"])
    state_selector.setStyleSheet("""
        QComboBox {
            background-color: #2C3E50;
            color: white;
            border-radius: 4px;
            padding: 5px;
            min-width: 200px;
        }
        QComboBox::drop-down {
            border-color: #34495E;
        }
        QComboBox QAbstractItemView {
            background-color: #2C3E50;
            color: white;
            selection-background-color: #1ABC9C;
        }
    """)
    
    # Animation control
    animate_btn = QPushButton("Start Animation")
    animate_btn.setStyleSheet("""
        QPushButton {
            background-color: #1ABC9C;
            color: white;
            border-radius: 4px;
            padding: 5px 15px;
        }
        QPushButton:hover {
            background-color: #16A085;
        }
    """)
    
    # Labels
    state_label = QLabel("Bell State:")
    state_label.setStyleSheet("color: white;")
    
    # Add widgets to controls
    controls_layout.addWidget(state_label)
    controls_layout.addWidget(state_selector)
    controls_layout.addStretch()
    controls_layout.addWidget(animate_btn)
    
    layout.addWidget(controls_frame)
    
    # Create matplotlib canvas for visualization
    canvas = MatplotlibCanvas(width=8, height=5)
    layout.addWidget(canvas)
    
    # Prepare subplot grid
    ax1 = canvas.fig.add_subplot(121, projection='3d')
    ax2 = canvas.fig.add_subplot(122, projection='3d')
    
    # Function to create a Bloch sphere
    def create_bloch_sphere(ax):
        # Draw Bloch sphere
        u = np.linspace(0, 2 * np.pi, 100)
        v = np.linspace(0, np.pi, 100)
        x = 1 * np.outer(np.cos(u), np.sin(v))
        y = 1 * np.outer(np.sin(u), np.sin(v))
        z = 1 * np.outer(np.ones(np.size(u)), np.cos(v))
        
        # Plot the surface with transparency
        ax.plot_surface(x, y, z, color='b', alpha=0.1)
        
        # Add axes
        ax.quiver(0, 0, 0, 1.5, 0, 0, color='r', arrow_length_ratio=0.1)
        ax.quiver(0, 0, 0, 0, 1.5, 0, color='g', arrow_length_ratio=0.1)
        ax.quiver(0, 0, 0, 0, 0, 1.5, color='b', arrow_length_ratio=0.1)
        
        # Add basis state labels
        ax.text(1.7, 0, 0, "|+x⟩", color='white')
        ax.text(0, 1.7, 0, "|+y⟩", color='white')
        ax.text(0, 0, 1.7, "|0⟩", color='white')
        ax.text(0, 0, -1.7, "|1⟩", color='white')
        
        # Set equal aspect ratio
        ax.set_box_aspect([1, 1, 1])
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.5, 1.5)
        ax.set_zlim(-1.5, 1.5)
        
        # Remove tick labels for cleaner look
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_zticklabels([])
        
        # Style for dark mode - fixed to use Matplotlib 3.x API
        ax.xaxis.pane.set_edgecolor("white")
        ax.yaxis.pane.set_edgecolor("white")
        ax.zaxis.pane.set_edgecolor("white")
        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.zaxis.pane.fill = False
        ax.set_facecolor('#253443')
    
    def update_visualization(bell_state_idx):
        ax1.clear()
        ax2.clear()
        
        # Create the Bloch spheres
        create_bloch_sphere(ax1)
        create_bloch_sphere(ax2)
        
        # Title for each Bloch sphere
        ax1.set_title("Qubit 1", color='white')
        ax2.set_title("Qubit 2", color='white')
        
        # Random points for visualization
        num_points = 100
        # Create random points on the Bloch sphere
        theta = np.random.uniform(0, np.pi, num_points)
        phi = np.random.uniform(0, 2 * np.pi, num_points)
        
        # Convert to Cartesian coordinates
        x1 = np.sin(theta) * np.cos(phi)
        y1 = np.sin(theta) * np.sin(phi)
        z1 = np.cos(theta)
        
        # Handle different Bell states
        bell_state = bell_state_idx
        if bell_state == 0:  # Φ+
            # Correlated in X and Z, anti-correlated in Y
            x2 = x1
            y2 = -y1
            z2 = z1
            title_text = "Bell State: Φ+ = (|00⟩ + |11⟩)/√2"
        elif bell_state == 1:  # Φ-
            # Anti-correlated in X and Y, correlated in Z
            x2 = -x1
            y2 = -y1
            z2 = z1
            title_text = "Bell State: Φ- = (|00⟩ - |11⟩)/√2"
        elif bell_state == 2:  # Ψ+
            # Correlated in X, anti-correlated in Y and Z
            x2 = x1
            y2 = -y1
            z2 = -z1
            title_text = "Bell State: Ψ+ = (|01⟩ + |10⟩)/√2"
        elif bell_state == 3:  # Ψ-
            # Anti-correlated in X, Y, and Z
            x2 = -x1
            y2 = -y1
            z2 = -z1
            title_text = "Bell State: Ψ- = (|01⟩ - |10⟩)/√2"
        
        # Plot the points
        qubit1_scatter = ax1.scatter(x1, y1, z1, color='yellow', s=10, alpha=0.7)
        
        # For qubit 2, show fewer points for clarity
        sample_indices = np.random.choice(num_points, 20, replace=False)
        qubit2_scatter = ax2.scatter(x2[sample_indices], y2[sample_indices], z2[sample_indices], 
                    color='yellow', s=30, alpha=0.7)
        
        # Add a special point to emphasize correlation
        highlight_idx = np.random.randint(0, num_points)
        highlight1 = ax1.scatter([x1[highlight_idx]], [y1[highlight_idx]], [z1[highlight_idx]], 
                    color='red', s=100, edgecolors='white')
        highlight2 = ax2.scatter([x2[highlight_idx]], [y2[highlight_idx]], [z2[highlight_idx]], 
                    color='red', s=100, edgecolors='white')
        
        # Set subtitle based on Bell state
        canvas.fig.suptitle(title_text, color='white', fontsize=14)
        
        # Draw the figure
        canvas.draw()
        
        return qubit1_scatter, qubit2_scatter, highlight1, highlight2
    
    # Animation timer
    animation_timer = QTimer()
    animation_active = [False]  # Using a list to allow modification in nested scope
    
    def toggle_animation():
        if animation_active[0]:
            animation_timer.stop()
            animate_btn.setText("Start Animation")
            animation_active[0] = False
        else:
            animation_timer.start(300)  # Update every 300 ms
            animate_btn.setText("Stop Animation")
            animation_active[0] = True
    
    animate_btn.clicked.connect(toggle_animation)
    animation_timer.timeout.connect(lambda: update_visualization(state_selector.currentIndex()))
    
    # Initialize the first visualization
    update_visualization(0)
    
    # Connect state selector to update function
    state_selector.currentIndexChanged.connect(update_visualization)
    
    # Description label with more detailed explanation
    description = QLabel(
        "<p>This visualization demonstrates quantum entanglement between two qubits in different Bell states.</p>"
        "<p>Bell states are maximally entangled quantum states of two qubits. When two qubits are entangled, "
        "measuring one qubit instantaneously determines the state of the other, regardless of the distance "
        "between them. This non-local correlation has no classical analog.</p>"
        "<p>The red points highlight a correlated measurement outcome - notice how measuring one qubit "
        "affects the other qubit's state based on the specific Bell state.</p>"
    )
    description.setWordWrap(True)
    description.setStyleSheet("color: #ECF0F1; margin: 20px 0;")
    layout.addWidget(description)
    
    # Set the layout and show the window
    ent_window.setLayout(layout)
    ent_window.show()
    
    # Keep references to prevent garbage collection
    ent_window.canvas = canvas
    ent_window.timer = animation_timer
    ent_window.controls = (state_selector, animate_btn)
    
    return ent_window


def visualize_superposition():
    """Function to visualize quantum superposition"""
    # Create a new window for superposition visualization
    super_window = QWidget()
    super_window.setWindowTitle("Quantum Superposition Visualization")
    super_window.setGeometry(200, 200, 900, 700)
    super_window.setStyleSheet("background-color: #1A2930;")
    
    layout = QVBoxLayout()
    
    # Title
    title = QLabel("Quantum Superposition Visualization")
    title.setFont(QFont('Arial', 16, QFont.Weight.Bold))
    title.setStyleSheet("color: #1ABC9C; margin-bottom: 20px;")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(title)
    
    # Controls for superposition parameters
    controls_frame = QFrame()
    controls_frame.setStyleSheet("background-color: #253443; border-radius: 6px; padding: 10px;")
    controls_layout = QGridLayout(controls_frame)
    
    # Alpha parameter (|0⟩ coefficient)
    alpha_slider = QSlider(Qt.Orientation.Horizontal)
    alpha_slider.setRange(0, 100)
    alpha_slider.setValue(71)  # sqrt(0.5) ≈ 0.71
    alpha_slider.setStyleSheet("""
        QSlider::groove:horizontal {
            height: 8px;
            background: #34495E;
            border-radius: 4px;
        }
        QSlider::handle:horizontal {
            background: #1ABC9C;
            width: 16px;
            margin: -4px 0;
            border-radius: 8px;
        }
    """)
    
    # Phase parameter
    phase_slider = QSlider(Qt.Orientation.Horizontal)
    phase_slider.setRange(0, 100)
    phase_slider.setValue(0)
    phase_slider.setStyleSheet(alpha_slider.styleSheet())
    
    # Alpha value display
    alpha_display = QLabel("α = 0.71")
    alpha_display.setStyleSheet("color: white; font-family: monospace;")
    
    # Beta value display (calculated from alpha)
    beta_display = QLabel("β = 0.71")
    beta_display.setStyleSheet("color: white; font-family: monospace;")
    
    # Phase display
    phase_display = QLabel("Phase = 0.00")
    phase_display.setStyleSheet("color: white; font-family: monospace;")
    
    # Labels
    alpha_label = QLabel("|0⟩ Coefficient (α):")
    alpha_label.setStyleSheet("color: white;")
    phase_label = QLabel("Relative Phase:")
    phase_label.setStyleSheet("color: white;")
    
    # Add all controls to the grid
    controls_layout.addWidget(alpha_label, 0, 0)
    controls_layout.addWidget(alpha_slider, 0, 1)
    controls_layout.addWidget(alpha_display, 0, 2)
    controls_layout.addWidget(QLabel("|1⟩ Coefficient (β):"), 1, 0)
    controls_layout.addWidget(beta_display, 1, 2)
    controls_layout.addWidget(phase_label, 2, 0)
    controls_layout.addWidget(phase_slider, 2, 1)
    controls_layout.addWidget(phase_display, 2, 2)
    
    layout.addWidget(controls_frame)
    
    # Create two canvases for different visualizations
    canvas_frame = QFrame()
    canvas_layout = QHBoxLayout(canvas_frame)
    
    # Bloch sphere visualization
    bloch_canvas = MatplotlibCanvas(width=4, height=4)
    
    # Probability visualization
    prob_canvas = MatplotlibCanvas(width=4, height=4)
    
    canvas_layout.addWidget(bloch_canvas)
    canvas_layout.addWidget(prob_canvas)
    layout.addWidget(canvas_frame)
    
    # Set up the Bloch sphere
    bloch_ax = bloch_canvas.fig.add_subplot(111, projection='3d')
    
    # Set up the probability visualization
    prob_ax = prob_canvas.fig.add_subplot(111)
    
    def create_bloch_sphere(ax):
        # Draw Bloch sphere
        u = np.linspace(0, 2 * np.pi, 100)
        v = np.linspace(0, np.pi, 100)
        x = 1 * np.outer(np.cos(u), np.sin(v))
        y = 1 * np.outer(np.sin(u), np.sin(v))
        z = 1 * np.outer(np.ones(np.size(u)), np.cos(v))
        
        # Plot the surface with transparency
        ax.plot_surface(x, y, z, color='b', alpha=0.1)
        
        # Add axes
        ax.quiver(0, 0, 0, 1.5, 0, 0, color='r', arrow_length_ratio=0.1)
        ax.quiver(0, 0, 0, 0, 1.5, 0, color='g', arrow_length_ratio=0.1)
        ax.quiver(0, 0, 0, 0, 0, 1.5, color='b', arrow_length_ratio=0.1)
        
        # Add basis state labels
        ax.text(1.7, 0, 0, "|+x⟩", color='white')
        ax.text(0, 1.7, 0, "|+y⟩", color='white')
        ax.text(0, 0, 1.7, "|0⟩", color='white')
        ax.text(0, 0, -1.7, "|1⟩", color='white')
        
        # Set equal aspect ratio
        ax.set_box_aspect([1, 1, 1])
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.5, 1.5)
        ax.set_zlim(-1.5, 1.5)
        
        # Remove tick labels for cleaner look
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_zticklabels([])
        
        # Style for dark mode - fixed to use Matplotlib 3.x API
        ax.xaxis.pane.set_edgecolor("white")
        ax.yaxis.pane.set_edgecolor("white")
        ax.zaxis.pane.set_edgecolor("white")
        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.zaxis.pane.fill = False
        ax.set_facecolor('#253443')
    
    def update_visualization():
        # Clear previous plots
        bloch_ax.clear()
        prob_ax.clear()
        
        # Create the Bloch sphere
        create_bloch_sphere(bloch_ax)
        
        # Get values from sliders
        alpha_val = alpha_slider.value() / 100.0
        beta_val = np.sqrt(1 - alpha_val**2)
        phase_val = phase_slider.value() * (2 * np.pi / 100.0)
        
        # Update displays
        alpha_display.setText(f"α = {alpha_val:.2f}")
        beta_display.setText(f"β = {beta_val:.2f}")
        phase_display.setText(f"Phase = {phase_val:.2f}")
        
        # Calculate state vector
        # |ψ⟩ = α|0⟩ + β·e^(iφ)|1⟩
        # Convert to Bloch sphere coordinates
        theta = 2 * np.arccos(alpha_val)
        phi = phase_val
        
        # Calculate point on Bloch sphere
        x = np.sin(theta) * np.cos(phi)
        y = np.sin(theta) * np.sin(phi)
        z = np.cos(theta)
        
        # Plot state vector on Bloch sphere
        bloch_ax.quiver(0, 0, 0, x, y, z, color='yellow', linewidth=3, arrow_length_ratio=0.15)
        bloch_ax.scatter([x], [y], [z], color='red', s=100)
        
        # Set title for Bloch sphere
        bloch_ax.set_title("Bloch Sphere Representation", color='white')
        
        # Plot probability amplitudes in bar chart
        states = ['|0⟩', '|1⟩']
        probs = [alpha_val**2, beta_val**2]
        
        # Real and imaginary components
        real_part = [alpha_val, beta_val * np.cos(phase_val)]
        imag_part = [0, beta_val * np.sin(phase_val)]
        
        # Bar positions
        bar_positions = np.arange(len(states))
        
        # Plot real parts
        prob_ax.bar(bar_positions, probs, width=0.5, color='#3498DB', alpha=0.7,
                  label='Probability')
        
        # Style the probability plot
        prob_ax.set_ylabel('Probability', color='white')
        prob_ax.set_title('Measurement Probabilities', color='white')
        prob_ax.set_ylim(0, 1)
        prob_ax.set_xticks(bar_positions)
        prob_ax.set_xticklabels(states)
        
        # Add text labels with probabilities
        for i, p in enumerate(probs):
            prob_ax.text(i, p + 0.05, f"{p:.2f}", ha='center', color='white')
        
        # Add equation of current state at the bottom
        eq_text = f"|ψ⟩ = {alpha_val:.2f}|0⟩ + "
        if phase_val == 0:
            eq_text += f"{beta_val:.2f}|1⟩"
        else:
            eq_text += f"{beta_val:.2f}e^{phase_val:.2f}i|1⟩"
        
        prob_ax.text(0.5, -0.15, eq_text, ha='center', color='white', 
                    transform=prob_ax.transAxes, fontsize=12)
        
        # Style plots for dark mode
        prob_ax.set_facecolor('#253443')
        for spine in prob_ax.spines.values():
            spine.set_color('white')
        prob_ax.tick_params(colors='white')
        
        # Update the canvases
        bloch_canvas.draw()
        prob_canvas.draw()
    
    # Connect sliders to update function
    alpha_slider.valueChanged.connect(update_visualization)
    phase_slider.valueChanged.connect(update_visualization)
    
    # Initial visualization
    update_visualization()
    
    # Description label
    description = QLabel(
        "<p>This visualization demonstrates quantum superposition, a fundamental concept in quantum mechanics "
        "where a quantum system can exist in multiple states simultaneously.</p>"
        "<p>The Bloch sphere (left) shows the quantum state as a point on the surface of the sphere. "
        "The north pole represents |0⟩, the south pole represents |1⟩, and all other points represent superpositions.</p>"
        "<p>The bar chart (right) shows the probability of measuring each basis state. "
        "Adjust the sliders to see how changing the amplitudes and relative phase affects the quantum state.</p>"
    )
    description.setWordWrap(True)
    description.setStyleSheet("color: #ECF0F1; margin: 20px 0;")
    layout.addWidget(description)
    
    # Set the layout and show the window
    super_window.setLayout(layout)
    super_window.show()
    
    # Keep references to prevent garbage collection
    super_window.bloch_canvas = bloch_canvas
    super_window.prob_canvas = prob_canvas
    super_window.controls = (alpha_slider, phase_slider)
    
    return super_window


def visualize_interference():
    """Function to visualize quantum interference effects"""
    # Create a new window for interference visualization
    interf_window = QWidget()
    interf_window.setWindowTitle("Quantum Interference Visualization")
    interf_window.setGeometry(200, 200, 900, 700)
    interf_window.setStyleSheet("background-color: #1A2930;")
    
    layout = QVBoxLayout()
    
    # Title
    title = QLabel("Quantum Interference Visualization")
    title.setFont(QFont('Arial', 16, QFont.Weight.Bold))
    title.setStyleSheet("color: #1ABC9C; margin-bottom: 20px;")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(title)
    
    # Description at the top
    intro = QLabel(
        "This visualization demonstrates quantum interference, a phenomenon where probability amplitudes "
        "can add constructively or destructively, unlike classical probabilities."
    )
    intro.setWordWrap(True)
    intro.setStyleSheet("color: #ECF0F1; margin-bottom: 15px;")
    layout.addWidget(intro)
    
    # Controls frame
    controls_frame = QFrame()
    controls_frame.setStyleSheet("background-color: #253443; border-radius: 6px; padding: 10px;")
    controls_layout = QGridLayout(controls_frame)
    
    # Phase controls for two paths
    path1_phase = QSlider(Qt.Orientation.Horizontal)
    path1_phase.setRange(0, 100)
    path1_phase.setValue(0)
    path1_phase.setStyleSheet("""
        QSlider::groove:horizontal {
            height: 8px;
            background: #34495E;
            border-radius: 4px;
        }
        QSlider::handle:horizontal {
            background: #1ABC9C;
            width: 16px;
            margin: -4px 0;
            border-radius: 8px;
        }
    """)
    
    path2_phase = QSlider(Qt.Orientation.Horizontal)
    path2_phase.setRange(0, 100)
    path2_phase.setValue(50)  # Default to π (out of phase)
    path2_phase.setStyleSheet(path1_phase.styleSheet())
    
    # Phase display labels
    path1_display = QLabel("Path 1 Phase = 0.00")
    path1_display.setStyleSheet("color: white; font-family: monospace;")
    
    path2_display = QLabel("Path 2 Phase = π")
    path2_display.setStyleSheet("color: white; font-family: monospace;")
    
    # Add controls to layout
    controls_layout.addWidget(QLabel("Path 1 Phase:"), 0, 0)
    controls_layout.addWidget(path1_phase, 0, 1)
    controls_layout.addWidget(path1_display, 0, 2)
    
    controls_layout.addWidget(QLabel("Path 2 Phase:"), 1, 0)
    controls_layout.addWidget(path2_phase, 1, 1)
    controls_layout.addWidget(path2_display, 1, 2)
    
    layout.addWidget(controls_frame)
    
    # Create matplotlib canvas for visualization
    canvas = MatplotlibCanvas(width=8, height=5)
    layout.addWidget(canvas)
    
    # Set up the figure with subplots
    gs = canvas.fig.add_gridspec(2, 2, height_ratios=[1, 1.5])
    ax_paths = canvas.fig.add_subplot(gs[0, :])
    ax_combined = canvas.fig.add_subplot(gs[1, :])
    
    def update_visualization():
        # Clear previous plots
        ax_paths.clear()
        ax_combined.clear()
        
        # Get phases from sliders (0 to 2π)
        phase1 = path1_phase.value() * (2 * np.pi / 100)
        phase2 = path2_phase.value() * (2 * np.pi / 100)
        
        # Update display labels
        if abs(phase1 - np.pi) < 0.1:
            path1_display.setText("Path 1 Phase = π")
        elif abs(phase1 - 2*np.pi) < 0.1 or phase1 < 0.1:
            path1_display.setText("Path 1 Phase = 0")
        else:
            path1_display.setText(f"Path 1 Phase = {phase1:.2f}")
            
        if abs(phase2 - np.pi) < 0.1:
            path2_display.setText("Path 2 Phase = π")
        elif abs(phase2 - 2*np.pi) < 0.1 or phase2 < 0.1:
            path2_display.setText("Path 2 Phase = 0")
        else:
            path2_display.setText(f"Path 2 Phase = {phase2:.2f}")
        
        # Create x values for the wave plot
        x = np.linspace(0, 10, 1000)
        
        # Create waves with the respective phases
        amplitude = 0.5
        wave1 = amplitude * np.sin(x - phase1)
        wave2 = amplitude * np.sin(x - phase2)
        
        # Combined wave (interference)
        combined = wave1 + wave2
        
        # Plot individual waves
        ax_paths.plot(x, wave1, color='#3498DB', label='Path 1')
        ax_paths.plot(x, wave2, color='#E74C3C', label='Path 2')
        ax_paths.set_title('Individual Path Amplitudes', color='white')
        ax_paths.legend()
        ax_paths.set_ylim(-1.1, 1.1)
        ax_paths.set_yticks([-1, -0.5, 0, 0.5, 1])
        
        # Plot combined wave (interference)
        ax_combined.plot(x, combined, color='#F1C40F', linewidth=2)
        ax_combined.set_title('Combined Amplitude (Interference)', color='white')
        ax_combined.set_ylim(-1.1, 1.1)
        ax_combined.set_yticks([-1, -0.5, 0, 0.5, 1])
        ax_combined.set_xlabel('Position', color='white')
        
        # Calculate the phase difference and interference type
        phase_diff = abs((phase1 - phase2) % (2 * np.pi))
        if phase_diff < 0.1 or abs(phase_diff - 2*np.pi) < 0.1:
            interf_type = "Constructive Interference"
        elif abs(phase_diff - np.pi) < 0.1:
            interf_type = "Destructive Interference"
        else:
            interf_type = "Partial Interference"
        
        ax_combined.set_title(f'Combined Amplitude: {interf_type}', color='white')
        
        # Style the plots for dark mode
        for ax in [ax_paths, ax_combined]:
            ax.set_facecolor('#253443')
            for spine in ax.spines.values():
                spine.set_color('white')
            ax.tick_params(colors='white')
            ax.grid(True, linestyle='--', alpha=0.3, color='white')
        
        # Update the canvas
        canvas.draw()
    
    # Connect sliders to update function
    path1_phase.valueChanged.connect(update_visualization)
    path2_phase.valueChanged.connect(update_visualization)
    
    # Initial visualization
    update_visualization()
    
    # Explanation text
    explanation = QLabel(
        "<p>Quantum interference is the phenomenon where probability amplitudes can add constructively "
        "or destructively, unlike classical probabilities.</p>"
        "<p>In this visualization:</p>"
        "<ul>"
        "<li>When the paths are in phase (0° or 360° difference), <b>constructive interference</b> occurs, "
        "maximizing the probability of detecting the particle.</li>"
        "<li>When the paths are out of phase (180° difference), <b>destructive interference</b> occurs, "
        "potentially canceling out and reducing the probability to zero.</li>"
        "</ul>"
        "<p>This is the fundamental principle behind phenomena like the double-slit experiment and quantum computing algorithms.</p>"
    )
    explanation.setWordWrap(True)
    explanation.setStyleSheet("color: #ECF0F1; margin: 20px 0;")
    layout.addWidget(explanation)
    
    # Set the layout and show the window
    interf_window.setLayout(layout)
    interf_window.show()
    
    # Keep references to prevent garbage collection
    interf_window.canvas = canvas
    interf_window.controls = (path1_phase, path2_phase)
    
    return interf_window


class QuantumVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Main window configuration
        self.setWindowTitle("Quantum Visualizer Premium")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: #0F2027;")
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Header section
        header = QFrame()
        header.setMaximumHeight(100)
        header_layout = QHBoxLayout(header)
        
        title_label = QLabel("Quantum Visualizer")
        title_label.setFont(QFont('Arial', 24, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #1ABC9C;")
        
        subtitle_label = QLabel("Advanced Quantum State Visualization Suite")
        subtitle_label.setFont(QFont('Arial', 12))
        subtitle_label.setStyleSheet("color: #ECF0F1;")
        
        title_container = QVBoxLayout()
        title_container.addWidget(title_label)
        title_container.addWidget(subtitle_label)
        
        header_layout.addLayout(title_container)
        header_layout.addStretch()
        
        # Optional: Add a logo
        # logo_label = QLabel()
        # logo_pixmap = QPixmap("quantum_logo.png")
        # logo_label.setPixmap(logo_pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio))
        # header_layout.addWidget(logo_label)
        
        main_layout.addWidget(header)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #2C3E50; max-height: 2px;")
        main_layout.addWidget(separator)
        
        # Content section
        content = QFrame()
        content.setStyleSheet("""
            QFrame {
                background-color: #1A2930;
                border-radius: 10px;
            }
        """)
        
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Left sidebar for buttons
        sidebar = QFrame()
        sidebar.setMaximumWidth(300)
        sidebar.setStyleSheet("background-color: transparent;")
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setSpacing(15)
        
        # Group buttons by category
        basic_group = QGroupBox("Basic Quantum Concepts")
        basic_group.setStyleSheet("""
            QGroupBox {
                color: #1ABC9C;
                font-weight: bold;
                border: 1px solid #2C3E50;
                border-radius: 6px;
                margin-top: 1ex;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        basic_layout = QVBoxLayout(basic_group)
        
        advanced_group = QGroupBox("Advanced Quantum Phenomena")
        advanced_group.setStyleSheet(basic_group.styleSheet())
        advanced_layout = QVBoxLayout(advanced_group)
        
        # Basic concept buttons
        btn_states = StyledButton("Quantum States", "states_icon.png")
        btn_states.clicked.connect(self.show_quantum_states)
        basic_layout.addWidget(btn_states)
        
        btn_bloch = StyledButton("Bloch Sphere", "bloch_icon.png")
        btn_bloch.clicked.connect(self.show_bloch)
        basic_layout.addWidget(btn_bloch)
        
        btn_superposition = StyledButton("Quantum Superposition", "super_icon.png")
        btn_superposition.clicked.connect(self.show_superposition)
        basic_layout.addWidget(btn_superposition)
        
        # Advanced concept buttons
        btn_entanglement = StyledButton("Entanglement Visualization", "entanglement_icon.png")
        btn_entanglement.clicked.connect(self.show_entanglement)
        advanced_layout.addWidget(btn_entanglement)
        
        btn_interference = StyledButton("Quantum Interference", "interf_icon.png")
        btn_interference.clicked.connect(self.show_interference)
        advanced_layout.addWidget(btn_interference)
        
        btn_circuit = StyledButton("Quantum Circuit Visualization", "circuit_icon.png")
        btn_circuit.clicked.connect(self.show_circuit)
        advanced_layout.addWidget(btn_circuit)
        
        # Add groups to sidebar
        sidebar_layout.addWidget(basic_group)
        sidebar_layout.addWidget(advanced_group)
        sidebar_layout.addStretch()
        
        # Info section at the bottom of sidebar
        info_frame = QFrame()
        info_frame.setStyleSheet("background-color: #253443; border-radius: 6px; padding: 10px;")
        info_layout = QVBoxLayout(info_frame)
        
        info_title = QLabel("Quantum Visualizer Premium")
        info_title.setStyleSheet("color: #1ABC9C; font-weight: bold;")
        
        info_label = QLabel("Version 2.0.0\nⓒ Quantum Labs 2025")
        info_label.setStyleSheet("color: #7F8C8D; font-size: 10px;")
        
        info_layout.addWidget(info_title)
        info_layout.addWidget(info_label)
        
        sidebar_layout.addWidget(info_frame)
        
        # Right content area with stacked widget for different views
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("""
            QStackedWidget {
                background-color: #253443;
                border-radius: 8px;
            }
        """)
        
        # Welcome screen
        welcome_page = QWidget()
        welcome_layout = QVBoxLayout(welcome_page)
        
        welcome_label = QLabel("Welcome to Quantum Visualizer Premium")
        welcome_label.setFont(QFont('Arial', 18, QFont.Weight.Bold))
        welcome_label.setStyleSheet("color: #ECF0F1;")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        description_label = QLabel(
            "Explore quantum phenomena through interactive visualizations. "
            "Select a visualization option from the sidebar to begin your quantum journey."
        )
        description_label.setWordWrap(True)
        description_label.setStyleSheet("color: #BDC3C7; font-size: 14px;")
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Feature cards (3x2 grid)
        features_grid = QGridLayout()
        features_grid.setSpacing(20)
        
        # Define feature cards
        features = [
            ("Quantum States", "Visualize common quantum states and their properties"),
            ("Bloch Sphere", "Explore the geometric representation of qubit states"),
            ("Quantum Superposition", "Understand how qubits can exist in multiple states simultaneously"),
            ("Quantum Entanglement", "Visualize the non-local correlations between entangled qubits"),
            ("Quantum Interference", "See how probability amplitudes can interfere constructively or destructively"),
            ("Quantum Circuits", "Design and visualize quantum gates and circuits")
        ]
        
        # Create feature cards
        row, col = 0, 0
        for title, desc in features:
            card = InfoPanel(title, desc)
            features_grid.addWidget(card, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        welcome_layout.addStretch()
        welcome_layout.addWidget(welcome_label)
        welcome_layout.addWidget(description_label)
        welcome_layout.addSpacing(30)
        welcome_layout.addLayout(features_grid)
        welcome_layout.addStretch()
        
        # Add welcome page to stack
        self.content_stack.addWidget(welcome_page)
        
        # Add widgets to content layout
        content_layout.addWidget(sidebar)
        content_layout.addWidget(self.content_stack, 1)  # 1 is the stretch factor
        
        main_layout.addWidget(content, 1)  # 1 is the stretch factor
        
        # Set the main layout
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        
        # Reference to keep visualization windows from being garbage collected
        self.open_windows = []
    
    def show_circuit(self):
        draw_circuit()
    
    def show_bloch(self):
        bloch_sphere()
    
    def show_quantum_states(self):
        window = visualize_quantum_states()
        self.open_windows.append(window)  # Keep reference
    
    def show_entanglement(self):
        window = visualize_entanglement()
        self.open_windows.append(window)  # Keep reference
    
    def show_superposition(self):
        window = visualize_superposition()
        self.open_windows.append(window)  # Keep reference
    
    def show_interference(self):
        window = visualize_interference()
        self.open_windows.append(window)  # Keep reference


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application-wide styles
    app.setStyle("Fusion")
    
    # Create and show the main window
    window = QuantumVisualizer()
    window.show()
    
    sys.exit(app.exec())