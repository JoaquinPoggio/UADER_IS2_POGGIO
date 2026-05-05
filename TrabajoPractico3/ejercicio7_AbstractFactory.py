from abc import ABC, abstractmethod

class Button(ABC):
    @abstractmethod
    def render(self):
        pass

class Window(ABC):
    @abstractmethod
    def render(self):
        pass

#Productos concretos Windows
class WindowsButton(Button):
    def render(self):
        return "Renderizando botón de Windows"
    
class WindowsWindow(Window):
    def render(self):
        return "Renderizando ventana de Windows"    
    
#Productos Concretos LINUX
class LinuxButton(Button):
    def render(self):
        return "Renderizando botón de Linux"
    
class LinuxWindow(Window):
    def render(self):
        return "Renderizando ventana de Linux"
    
#ABSTRACT FACTOTY USO
class GUIFactory(ABC):
    @abstractmethod
    def create_button(self):
        pass
    
    @abstractmethod
    def create_window(self):
        pass

class WindowsFactory(GUIFactory):
    def create_button(self):
        return WindowsButton()
    
    def create_window(self):
        return WindowsWindow()

class LinuxFactory(GUIFactory):
    def create_button(self):
        return LinuxButton()
    
    def create_window(self):
        return LinuxWindow()

def render_ui(factory: GUIFactory):
    button = factory.create_button()
    window = factory.create_window()
    print(button.render())
    print(window.render())

#se elige una o la otra dependiendo del sistema operativo
render_ui(WindowsFactory())
render_ui(LinuxFactory()) 