import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QLineEdit, QHBoxLayout, QStackedWidget, QSizePolicy, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.patches import Polygon
from matplotlib.text import Annotation
import numpy as np
from shapely.geometry import Polygon as ShapelyPolygon, Point, LineString
from shapely.ops import cascaded_union
from shapely.errors import TopologicalError
import matplotlib.pyplot as plt


class PlotCanvas(FigureCanvas):
    point_selected = pyqtSignal(str)

    def __init__(self, num_polygons, parent=None, width=5, height=4, dpi=100):
        self.fig, self.ax = plt.subplots(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.parent = parent
        self.coordinates = {'start': None, 'goal': None}
        self.polygons = self.generatePolygons(num_polygons)
        self.cid = self.mpl_connect('button_press_event', self.on_click)
        self.annot = None
        self.goal_selected = False  # Flag to track goal selection

    def generatePolygons(self, num_polygons):
        existing_polygons = []
        polygons = []
        for _ in range(num_polygons):
            new_polygon = self.generate_random_polygon(existing_polygons)
            polygons.append(new_polygon)
            existing_polygons.append(ShapelyPolygon(new_polygon))
        self.plotPolygons(polygons)
        return existing_polygons

    def generate_random_polygon(self, existing_polygons):
        while True:
            num_edges = np.random.randint(3, 8)  # Random number of edges between 3 and 7
            polygon = []
            for _ in range(num_edges):
                x, y = np.random.rand(2) * 10  # Random x, y coordinates between 0 and 10
                polygon.append([x, y])

            try:
                # Check if the new polygon overlaps with any existing polygons
                new_polygon = ShapelyPolygon(polygon)
                overlap = any(new_polygon.intersects(ShapelyPolygon(existing)) for existing in existing_polygons)
                if not overlap and new_polygon.is_simple:
                    return polygon
            except (ValueError, TopologicalError):
                # Catch any exceptions related to invalid geometries or topology errors
                pass

    def plotPolygons(self, polygons):
        self.ax.clear()
        for polygon in polygons:
            self.ax.add_patch(Polygon(polygon, closed=True, fill=None, edgecolor='b'))
        self.ax.autoscale()
        self.ax.set_aspect('equal', 'box')
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_title('Non-overlapping Simple Polygons')
        self.ax.grid(True)
        self.draw()

    def on_click(self, event):
        if event.inaxes == self.ax:
            x, y = event.xdata, event.ydata
            clicked_point = Point(x, y)
            clicked_inside_polygon = False
            for polygon in self.polygons:
                if polygon.contains(clicked_point):
                    clicked_inside_polygon = True
                    break
            if clicked_inside_polygon:
                QMessageBox.warning(self.parent, "Warning", "Please select a point outside the polygons.")
            else:
                if self.coordinates['start'] is None:
                    self.coordinates['start'] = (x, y)
                    self.point_selected.emit('start')
                    self.annotate_point(x, y, 'Start')
                elif self.coordinates['goal'] is None and not self.goal_selected:
                    self.coordinates['goal'] = (x, y)
                    self.point_selected.emit('goal')
                    self.annotate_point(x, y, 'Goal')

    def annotate_point(self, x, y, label):
        if self.annot:
            self.annot.remove()
        self.annot = Annotation(label, (x, y), xytext=(5,-5), textcoords='offset points', ha='left', va='bottom', bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5))
        self.ax.add_artist(self.annot)
        self.draw()


class PageB(QWidget):
    def __init__(self, num_polygons, parent=None):
        super().__init__(parent)
        self.back_button = QPushButton('Back')
        self.back_button.clicked.connect(parent.showPageA)

        self.canvas = PlotCanvas(num_polygons, parent)
        self.goal_selected = False  # Initialize goal_selected

        self.selection_label = QLabel('Select a point:')
        self.selection_text = QLabel('Select start and goal points')

        self.done_button = QPushButton('Done')
        self.done_button.clicked.connect(self.doneClicked)

        layout = QVBoxLayout()
        layout.addWidget(self.back_button)
        layout.addWidget(self.selection_label)
        layout.addWidget(self.selection_text)
        layout.addWidget(self.canvas)
        layout.addWidget(self.done_button)
        self.setLayout(layout)

        # Connect the point_selected signal from the canvas to the update_selection_text method
        self.canvas.point_selected.connect(self.update_selection_text)

    def update_selection_text(self, point_type):
        if point_type == 'start':
            self.selection_text.setText('Select goal point')
        elif point_type == 'goal':
            self.goal_selected = True  # Update goal_selected flag
            self.selection_text.setText('Press Done to proceed')

    def doneClicked(self):
        if not self.goal_selected:
            QMessageBox.warning(self, "Error", "Please select the goal point.")
        else:
            # Find the parent MainWindow instance
            main_window = self.findParentMainWindow()
            if main_window:
                main_window.showPageC(self.canvas.coordinates)

    def findParentMainWindow(self):
        parent = self.parent()
        while parent:
            if isinstance(parent, MainWindow):
                return parent
            parent = parent.parent()
        return None


class PageC(QWidget):
    def __init__(self, coordinates, parent=None):
        super().__init__(parent)
        self.coordinates = coordinates
        self.label_start = QLabel('Start Coordinate:')
        self.label_goal = QLabel('Goal Coordinate:')
        self.label_start_value = QLabel(f'{self.coordinates["start"]}')
        self.label_goal_value = QLabel(f'{self.coordinates["goal"]}')
        self.back_button = QPushButton('Back')
        self.back_button.clicked.connect(parent.showPageB)

        self.show_path_button = QPushButton('Show the optimal path from start to goal')
        self.show_path_button.clicked.connect(self.showPathClicked)

        # Set font size
        font = QFont()
        font.setPointSize(12)
        self.label_start.setFont(font)
        self.label_goal.setFont(font)
        self.label_start_value.setFont(font)
        self.label_goal_value.setFont(font)
        self.back_button.setFont(font)
        self.show_path_button.setFont(font)

        layout = QVBoxLayout()
        layout.addWidget(self.label_start)
        layout.addWidget(self.label_start_value)
        layout.addWidget(self.label_goal)
        layout.addWidget(self.label_goal_value)
        layout.addWidget(self.show_path_button)
        layout.addWidget(self.back_button)
        self.setLayout(layout)

    def showPathClicked(self):
        main_window = self.findParentMainWindow()
        if main_window:
            main_window.showPageD(self.coordinates)

    def findParentMainWindow(self):
        parent = self.parent()
        while parent:
            if isinstance(parent, MainWindow):
                return parent
            parent = parent.parent()
        return None


class PageD(QWidget):
    def __init__(self, coordinates, parent=None):
        super().__init__(parent)
        self.coordinates = coordinates
        self.canvas = PlotCanvas(0, parent)
        self.back_button = QPushButton('Back')
        self.back_button.clicked.connect(self.goBackToPageC)  # Connect to the new method

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.back_button)
        self.setLayout(layout)

        self.plot_path()

    def plot_path(self):
        start_point = Point(self.coordinates['start'])
        goal_point = Point(self.coordinates['goal'])

        all_polygons = [ShapelyPolygon(polygon) for polygon in self.canvas.polygons]
        combined_polygons = cascaded_union(all_polygons)

        # Compute the shortest path
        shortest_path = LineString([start_point, goal_point])
        intersection = combined_polygons.intersection(shortest_path)
        if not intersection.is_empty:
            if isinstance(intersection, Point):
                shortest_path = LineString([start_point, intersection, goal_point])
            elif isinstance(intersection, LineString):
                if intersection.length < shortest_path.length:
                    shortest_path = intersection

        # Plot the polygons
        self.canvas.plotPolygons([polygon.exterior.coords.xy for polygon in all_polygons])

        # Plot the start and goal points
        start_x, start_y = start_point.xy
        goal_x, goal_y = goal_point.xy
        self.canvas.ax.plot(start_x, start_y, 'go', markersize=10, label='Start')
        self.canvas.ax.plot(goal_x, goal_y, 'ro', markersize=10, label='Goal')

        # Plot the shortest path
        shortest_path_x, shortest_path_y = shortest_path.xy
        self.canvas.ax.plot(shortest_path_x, shortest_path_y, 'k-', linewidth=2, label='Shortest Path')
        self.canvas.ax.legend()

        self.canvas.draw()

    def goBackToPageC(self):
        main_window = self.findParentMainWindow()
        if main_window:
            main_window.showPageC(self.coordinates)

    def findParentMainWindow(self):
        parent = self.parent()
        while parent:
            if isinstance(parent, MainWindow):
                return parent
            parent = parent.parent()
        return None


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Polygon Generator')
        self.setFixedSize(800, 600)  # Fixed size for the window

        self.stacked_widget = QStackedWidget()
        self.pageA = PageA(self)
        self.stacked_widget.addWidget(self.pageA)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)

    def showPageB(self):
        num_polygons_text = self.pageA.numPolygons()
        if not num_polygons_text:
            QMessageBox.warning(self, "Error", "Please enter a valid number of polygons.")
            return
        num_polygons = int(num_polygons_text)
        if num_polygons > 0:
            self.pageB = PageB(num_polygons, self)
            self.stacked_widget.addWidget(self.pageB)
            self.stacked_widget.setCurrentWidget(self.pageB)

    def showPageC(self, coordinates):
        pageC = PageC(coordinates, self)
        self.stacked_widget.addWidget(pageC)
        self.stacked_widget.setCurrentWidget(pageC)

    def showPageD(self, coordinates):
        pageD = PageD(coordinates, self)
        self.stacked_widget.addWidget(pageD)
        self.stacked_widget.setCurrentWidget(pageD)

    def showPageA(self):
        self.stacked_widget.setCurrentWidget(self.pageA)


class PageA(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.num_polygons_label = QLabel('Enter the number of polygons:')
        self.num_polygons_input = QLineEdit()
        self.generate_button = QPushButton('Generate')
        self.generate_button.clicked.connect(parent.showPageB)

        # Set size policy for input box and button
        self.num_polygons_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.generate_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Set font size
        font = QFont()
        font.setPointSize(12)
        self.num_polygons_label.setFont(font)
        self.num_polygons_input.setFont(font)
        self.generate_button.setFont(font)

        # Set margins and spacing for layout
        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)  # 2px padding on all sides
        layout.setSpacing(2)  # 2px spacing between widgets

        # Horizontal layout for label, input box, and button
        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.num_polygons_label)
        hbox1.addWidget(self.num_polygons_input)
        layout.addLayout(hbox1)

        # Second line for the generate button
        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.generate_button)
        layout.addLayout(hbox2)

        # Adjust widget widths to fit content
        self.adjustWidgetWidths()

        self.setLayout(layout)

    def adjustWidgetWidths(self):
        # Adjust width of input box and buttons based on content
        input_width = self.num_polygons_input.sizeHint().width() + 20  # Add a small margin
        self.num_polygons_input.setMinimumWidth(input_width)
        button_width = self.generate_button.sizeHint().width() + 20  # Add a small margin
        self.generate_button.setMinimumWidth(button_width)

    def numPolygons(self):
        return self.num_polygons_input.text().strip()  # Strip leading and trailing whitespace


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()