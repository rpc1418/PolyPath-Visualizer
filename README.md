# **PolyPath - PyQt5 app for visualizing polygons and calculating shortest paths.**

![GitHub repo size](https://img.shields.io/github/repo-size/rpc1418/PolyPath-Visualizer) ![License](https://img.shields.io/github/license/rpc1418/PolyPath-Visualizer) ![Contributors](https://img.shields.io/github/contributors/rpc1418/PolyPath-Visualizer)


## 🧩 PyQt5 Polygon Visualization Application

This PyQt5 application generates and visualizes **non-overlapping simple polygons**. Users can input the number of polygons they wish to generate and select **start** and **goal** points within these polygons.

The application is organized into multiple pages, managed by a `QStackedWidget`:

### 🔷 PageA:
- Input the number of polygons to generate.

### 🔷 PageB:
- Select the **start** and **goal** points within the generated polygons.

### 🔷 PageC:
- Displays the selected start and goal coordinates.
- Option to visualize the optimal path from start to goal.

### 🔷 PageD:
- Visualizes the polygons, start/goal points, and the **shortest path** between them using `matplotlib`.

---

## 🛠️ Technology Stack
- **PyQt5**: For creating the GUI components and managing multiple pages.
- **matplotlib**: For plotting and visualizing the polygons and paths.
- **Shapely**: For geometric calculations, such as checking for intersections and computing the shortest path.

---

This tool provides an interactive way to visualize geometric shapes, navigate through them, and calculate paths using advanced geometric principles.
