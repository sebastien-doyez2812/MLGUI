from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtCore import Qt
import OpenGL.GL as gl
from OpenGL.GLU import gluPerspective

class Segmentation3DViewer(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.rotation_x = -30.0  
        self.rotation_y = 45.0
        self.zoom = -6.0        
        
        self.last_pos = None

    def initializeGL(self):
        gl.glClearColor(0.12, 0.12, 0.12, 1.0)
        gl.glEnable(gl.GL_DEPTH_TEST)

    def resizeGL(self, w, h):
        gl.glViewport(0, 0, w, h)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        
        aspect = w / h if h > 0 else 1.0
        gluPerspective(45.0, aspect, 0.1, 100.0)
        
        gl.glMatrixMode(gl.GL_MODELVIEW)

    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glLoadIdentity()

        gl.glTranslatef(0.0, 0.0, self.zoom)       
        gl.glRotatef(self.rotation_x, 1.0, 0.0, 0.0) 
        gl.glRotatef(self.rotation_y, 0.0, 1.0, 0.0) 

        # --- GRILLE 3D ---
        gl.glBegin(gl.GL_LINES)
        
        size = 3.0
        step = 0.5

        gl.glColor3f(0.25, 0.25, 0.25)
        i = -size
        while i <= size:
            if i != 0: 
                gl.glVertex3f(-size, 0.0, i)
                gl.glVertex3f(size, 0.0, i)
                gl.glVertex3f(i, 0.0, -size)
                gl.glVertex3f(i, 0.0, size)
            i += step

        # Axis Red X:
        gl.glColor3f(0.8, 0.2, 0.2)
        gl.glVertex3f(-size, 0.0, 0.0)
        gl.glVertex3f(size, 0.0, 0.0)

        # Axis Blue Z:
        gl.glColor3f(0.2, 0.2, 0.8)
        gl.glVertex3f(0.0, 0.0, -size)
        gl.glVertex3f(0.0, 0.0, size)

        gl.glEnd()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.last_pos is not None and event.buttons() == Qt.MouseButton.LeftButton:
            dx = event.pos().x() - self.last_pos.x()
            dy = event.pos().y() - self.last_pos.y()

            self.rotation_y += dx * 0.5
            self.rotation_x += dy * 0.5

            self.last_pos = event.pos()
            self.update() 

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_pos = None

    def wheelEvent(self, event):
        angle_delta = event.angleDelta().y()
        if angle_delta > 0:
            self.zoom += 0.3 
        else:
            self.zoom -= 0.3 
            
        self.update()