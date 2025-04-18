from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
import matplotlib.colors as mcolors

class MemoryVisualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.figure = Figure(figsize=(10, 8), facecolor='#2b2b2b')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
        """)
        
        # Create main layout
        self.layout = QVBoxLayout()
        
        # Add info panel
        self.info_panel = QHBoxLayout()
        self.memory_usage_label = QLabel("Memory Usage: 0%")
        self.object_count_label = QLabel("Objects: 0")
        self.fragmentation_label = QLabel("Fragmentation: 0%")
        
        # Style the labels
        for label in [self.memory_usage_label, self.object_count_label, self.fragmentation_label]:
            label.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    background-color: #3b3b3b;
                    padding: 5px 10px;
                    border-radius: 5px;
                }
            """)
        
        self.info_panel.addWidget(self.memory_usage_label)
        self.info_panel.addWidget(self.object_count_label)
        self.info_panel.addWidget(self.fragmentation_label)
        self.info_panel.addStretch()
        
        self.layout.addLayout(self.info_panel)
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)
        
        # Set custom style
        plt.style.use('dark_background')
        self.colors = {
            'root': '#00ff9f',      # Bright Green
            'reachable': '#00b8ff',  # Bright Blue
            'unreachable': '#ff4d4d', # Bright Red
            'free': '#404040',       # Dark Gray
            'text': '#ffffff',       # White
            'background': '#2b2b2b',  # Dark Background
            'grid': '#404040',       # Grid Color
            'relationship': '#ffd700', # Gold for relationships
            'node': '#ff69b4',       # Pink for nodes
            'node_border': '#ff1493', # Deep Pink for node borders
            'text_bg': '#3b3b3b'     # Background for text
        }

    def format_size(self, size_mb):
        """Convert size in MB to human readable format"""
        if size_mb >= 1024:
            return f"{size_mb/1024:.1f} GB"
        return f"{size_mb} MB"

    def update_visualization(self, memory_state):
        self.figure.clear()
        
        # Create subplots with adjusted height ratios
        gs = self.figure.add_gridspec(2, 1, height_ratios=[1.5, 1])
        ax1 = self.figure.add_subplot(gs[0])  # Memory map
        ax2 = self.figure.add_subplot(gs[1])  # Object relationships
        
        # Set background color for subplots
        for ax in [ax1, ax2]:
            ax.set_facecolor(self.colors['background'])
            ax.grid(True, color=self.colors['grid'], alpha=0.2)
        
        # Get memory state
        total_memory = memory_state['total_memory']
        used_memory = memory_state['used_memory']
        objects = memory_state['objects']
        root_objects = memory_state['root_objects']
        
        # Calculate statistics
        object_count = len(objects)
        fragmentation = self.calculate_fragmentation(memory_state)
        
        # Update info panel with formatted sizes
        self.memory_usage_label.setText(f"Memory Usage: {self.format_size(used_memory)} / {self.format_size(total_memory)} ({used_memory/total_memory*100:.1f}%)")
        self.object_count_label.setText(f"Objects: {object_count}")
        self.fragmentation_label.setText(f"Fragmentation: {fragmentation:.1f}%")
        
        # Create memory map visualization
        memory_map = np.zeros(total_memory)
        current_pos = 0
        
        # Plot memory blocks
        for obj_id, obj in objects.items():
            color = self.colors['root'] if obj_id in root_objects else self.colors['reachable']
            if not obj.is_reachable:
                color = self.colors['unreachable']
            
            # Fill memory map
            memory_map[current_pos:current_pos + obj.size] = obj_id
            current_pos += obj.size
            
            # Plot object block with gradient
            gradient = np.linspace(0, 1, 256).reshape(1, -1)
            gradient = np.vstack((gradient, gradient))
            ax1.imshow(gradient, aspect='auto', extent=[current_pos - obj.size, current_pos, 0, 1],
                      cmap=plt.cm.colors.LinearSegmentedColormap.from_list('custom', [color, mcolors.to_rgba(color, 0.7)]))
            
            # Add object details with formatted size
            details = f'Obj {obj_id}\nSize: {self.format_size(obj.size)}\nRefs: {len(obj.references)}'
            ax1.text(current_pos - obj.size/2, 0.5, details, 
                    ha='center', va='center', color=self.colors['text'],
                    fontsize=8, bbox=dict(facecolor=self.colors['text_bg'], alpha=0.8, edgecolor='none'))
        
        # Plot free memory
        if current_pos < total_memory:
            ax1.barh(0, total_memory - current_pos, left=current_pos, 
                    color=self.colors['free'], alpha=0.3)
        
        # Plot object relationships
        self.plot_relationships(ax2, objects, root_objects)
        
        # Set plot properties
        ax1.set_title('Memory Map Visualization', pad=20, color=self.colors['text'])
        ax1.set_xlabel('Memory Address', color=self.colors['text'])
        ax1.set_ylim(-1, 1)
        ax1.set_xlim(0, total_memory)
        ax1.set_yticks([])
        
        # Add legend
        legend_elements = [
            Rectangle((0, 0), 1, 1, facecolor=self.colors['root'], label='Root Objects'),
            Rectangle((0, 0), 1, 1, facecolor=self.colors['reachable'], label='Reachable Objects'),
            Rectangle((0, 0), 1, 1, facecolor=self.colors['unreachable'], label='Unreachable Objects'),
            Rectangle((0, 0), 1, 1, facecolor=self.colors['free'], label='Free Memory')
        ]
        ax1.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1, 1.15),
                  facecolor=self.colors['text_bg'], edgecolor='none', labelcolor=self.colors['text'])
        
        # Adjust layout
        self.figure.tight_layout()
        self.canvas.draw()

    def plot_relationships(self, ax, objects, root_objects):
        # Create a simple graph visualization of object relationships
        y_positions = {}
        current_y = 0
        
        # Calculate total number of objects for spacing
        total_objects = len(objects)
        if total_objects == 0:
            return
            
        # Calculate spacing between objects
        spacing = 1.0 / (total_objects + 1)
        
        # Position objects vertically with even spacing
        for obj_id in root_objects:
            y_positions[obj_id] = current_y
            current_y += spacing
        
        # Position other objects
        for obj_id, obj in objects.items():
            if obj_id not in y_positions:
                y_positions[obj_id] = current_y
                current_y += spacing
        
        # Plot objects and relationships
        for obj_id, obj in objects.items():
            # Plot object node with enhanced styling
            color = self.colors['root'] if obj_id in root_objects else self.colors['reachable']
            if not obj.is_reachable:
                color = self.colors['unreachable']
            
            # Draw node with border
            ax.plot(0, y_positions[obj_id], 'o', color=color, markersize=12,
                   markeredgecolor=self.colors['node_border'], markeredgewidth=2)
            
            # Add object details with better formatting
            details = f'Obj {obj_id}\n{self.format_size(obj.size)}'
            ax.text(0.1, y_positions[obj_id], details, 
                   ha='left', va='center', color=self.colors['text'],
                   fontsize=8, bbox=dict(facecolor=self.colors['text_bg'], 
                                       alpha=0.8, edgecolor='none',
                                       pad=2))
            
            # Plot relationships with curved lines
            for ref_id in obj.references:
                if ref_id in y_positions:
                    # Create curved line
                    x = np.linspace(0, 1, 100)
                    y = np.interp(x, [0, 1], [y_positions[obj_id], y_positions[ref_id]])
                    # Add some curve to the line
                    y += 0.1 * np.sin(x * np.pi)
                    ax.plot(x, y, color=self.colors['relationship'], alpha=0.3, linewidth=1)
        
        # Set plot properties
        ax.set_title('Object Relationships', pad=20, color=self.colors['text'])
        ax.set_xlim(-0.2, 1.2)  # Increased x-axis range for better text placement
        ax.set_ylim(-spacing, 1 + spacing)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.grid(False)

    def calculate_fragmentation(self, memory_state):
        total_memory = memory_state['total_memory']
        used_memory = memory_state['used_memory']
        objects = memory_state['objects']
        
        if not objects:
            return 0.0
            
        # Calculate total free memory
        free_memory = total_memory - used_memory
        
        # Calculate fragmentation as percentage of free memory
        if free_memory == 0:
            return 0.0
            
        return (free_memory / total_memory) * 100 