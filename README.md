# Garbage Collection Simulator

A visual simulator for understanding garbage collection in operating systems. This project demonstrates how memory management and garbage collection work in a modern operating system environment.

## Features

- Interactive GUI with real-time memory visualization
- Simulated memory allocation and deallocation
- Mark-and-Sweep garbage collection algorithm
- Visual representation of memory objects and their states
- Memory usage statistics and monitoring

## Requirements

- Python 3.7+
- PyQt5
- Matplotlib
- NumPy

## Installation

1. Clone this repository
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python main.py
```

2. Using the interface:
   - Use the "Add Object" button to allocate new memory objects
   - Adjust the object size using the spin box (1-100 units)
   - Click "Run Garbage Collection" to perform garbage collection
   - Watch the visualization update in real-time

## Visualization Guide

The memory visualization shows:
- Green blocks: Root objects (directly accessible)
- Blue blocks: Reachable objects (accessible through references)
- Red blocks: Unreachable objects (garbage)
- Memory usage percentage at the top
- Object IDs for easy reference

## How It Works

1. **Memory Allocation**:
   - Objects are allocated with random sizes
   - Each object can reference other objects
   - Some objects are marked as root objects

2. **Garbage Collection**:
   - Uses Mark-and-Sweep algorithm
   - Mark phase: Identifies all reachable objects from root objects
   - Sweep phase: Removes unreachable objects
   - Updates memory map and statistics

3. **Visualization**:
   - Real-time updates of memory state
   - Color-coded objects based on their status
   - Memory usage statistics
   - Object relationships

## Technical Details

- Total simulated memory: 1000 units
- Object size range: 1-100 units
- Random object references: 0-3 per object
- Root object probability: 30%
- Reachable object probability: 70%

## Contributing

Feel free to submit issues and enhancement requests! 