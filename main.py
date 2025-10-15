import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QTextEdit, QLabel, QDialog, QCheckBox, QTabWidget,
    QMessageBox, QGroupBox, QComboBox, QLineEdit
)
from PyQt6.QtCore import Qt
from sistema_fat import SistemaFAT


class DialogoCrearArchivo(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Crear Archivo")
        self.setMinimumWidth(500)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Nombre del archivo:"))
        self.entrada_nombre = QLineEdit()
        layout.addWidget(self.entrada_nombre)
        layout.addWidget(QLabel("Contenido:"))
        self.entrada_contenido = QTextEdit()
        self.entrada_contenido.setMinimumHeight(200)
        layout.addWidget(self.entrada_contenido)
        botones = QHBoxLayout()
        btn_crear = QPushButton("Crear")
        btn_crear.clicked.connect(self.accept)
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        botones.addWidget(btn_crear)
        botones.addWidget(btn_cancelar)
        layout.addLayout(botones)
        self.setLayout(layout)

    def obtener_datos(self):
        return self.entrada_nombre.text(), self.entrada_contenido.toPlainText()


class DialogoVerArchivo(QDialog):
    def __init__(self, archivo, contenido, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Archivo: {archivo['nombre']}")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        layout = QVBoxLayout()
        grupo_meta = QGroupBox("Metadatos")
        layout_meta = QVBoxLayout()
        layout_meta.addWidget(QLabel(f"<b>Nombre:</b> {archivo['nombre']}"))
        layout_meta.addWidget(QLabel(f"<b>Owner:</b> {archivo['propietario']}"))
        layout_meta.addWidget(QLabel(f"<b>Tamaño:</b> {archivo['cantidad_caracteres']} caracteres"))
        layout_meta.addWidget(QLabel(f"<b>Creado:</b> {archivo['fecha_creacion']}"))
        layout_meta.addWidget(QLabel(f"<b>Modificado:</b> {archivo['fecha_modificacion']}"))
        permisos_texto = "Permisos:\n"
        for usuario, perms in archivo.get('permisos', {}).items():
            permisos_texto += f"  • {usuario}: "
            permisos_lista = []
            if perms.get('lectura'):
                permisos_lista.append("Lectura")
            if perms.get('escritura'):
                permisos_lista.append("Escritura")
            permisos_texto += ", ".join(permisos_lista) + "\n"
        layout_meta.addWidget(QLabel(permisos_texto))
        grupo_meta.setLayout(layout_meta)
        layout.addWidget(grupo_meta)
        layout.addWidget(QLabel("<b>Contenido:</b>"))
        texto_contenido = QTextEdit()
        texto_contenido.setPlainText(contenido)
        texto_contenido.setReadOnly(True)
        layout.addWidget(texto_contenido)
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.accept)
        layout.addWidget(btn_cerrar)
        self.setLayout(layout)


class DialogoModificarArchivo(QDialog):
    def __init__(self, nombre, contenido_actual, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Modificar: {nombre}")
        self.setMinimumWidth(500)
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"<b>Archivo:</b> {nombre}"))
        layout.addWidget(QLabel("Contenido actual:"))
        texto_actual = QTextEdit()
        texto_actual.setPlainText(contenido_actual)
        texto_actual.setReadOnly(True)
        texto_actual.setMaximumHeight(150)
        layout.addWidget(texto_actual)
        layout.addWidget(QLabel("Nuevo contenido:"))
        self.entrada_nuevo = QTextEdit()
        self.entrada_nuevo.setMinimumHeight(200)
        layout.addWidget(self.entrada_nuevo)
        botones = QHBoxLayout()
        btn_guardar = QPushButton("Guardar")
        btn_guardar.clicked.connect(self.accept)
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        botones.addWidget(btn_guardar)
        botones.addWidget(btn_cancelar)
        layout.addLayout(botones)
        self.setLayout(layout)

    def obtener_contenido(self):
        return self.entrada_nuevo.toPlainText()


class DialogoPermisos(QDialog):
    def __init__(self, nombre_archivo, usuarios, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Gestionar Permisos: {nombre_archivo}")
        self.setMinimumWidth(400)
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"<b>Archivo:</b> {nombre_archivo}"))
        layout.addWidget(QLabel("Usuario:"))
        self.combo_usuarios = QComboBox()
        self.combo_usuarios.addItems(usuarios)
        layout.addWidget(self.combo_usuarios)
        self.check_lectura = QCheckBox("Permiso de Lectura")
        self.check_escritura = QCheckBox("Permiso de Escritura")
        layout.addWidget(self.check_lectura)
        layout.addWidget(self.check_escritura)
        botones = QHBoxLayout()
        btn_asignar = QPushButton("Asignar")
        btn_asignar.clicked.connect(self.accept)
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        botones.addWidget(btn_asignar)
        botones.addWidget(btn_cancelar)
        layout.addLayout(botones)
        self.setLayout(layout)

    def obtener_datos(self):
        return (self.combo_usuarios.currentText(),
                self.check_lectura.isChecked(),
                self.check_escritura.isChecked())



class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.sistema = SistemaFAT()
        self.inicializar_interfaz()

    def inicializar_interfaz(self):
        self.setWindowTitle("Sistema de Archivos FAT - Simulador")
        self.setMinimumSize(900, 600)
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_principal = QVBoxLayout(widget_central)

        encabezado = QLabel("<h2>Sistema de Archivos FAT</h2>")
        encabezado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_principal.addWidget(encabezado)

        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("<b>Seleccionar usuario:</b>"))
        self.selector_usuario = QComboBox()
        self.selector_usuario.addItems(self.sistema.usuarios)
        self.selector_usuario.currentTextChanged.connect(self.cambiar_usuario)
        selector_layout.addWidget(self.selector_usuario)
        self.label_usuario = QLabel(f"Usuario actual: <b>{self.sistema.usuario_actual}</b>")
        selector_layout.addWidget(self.label_usuario)
        layout_principal.addLayout(selector_layout)

        self.pestanas = QTabWidget()

        # Tab Archivos
        tab_archivos = QWidget()
        layout_archivos = QVBoxLayout(tab_archivos)
        self.lista_archivos = QListWidget()
        self.lista_archivos.itemDoubleClicked.connect(self.abrir_archivo)
        layout_archivos.addWidget(QLabel("<b>Archivos:</b>"))
        layout_archivos.addWidget(self.lista_archivos)
        botones_archivos = QHBoxLayout()
        btn_crear = QPushButton("Crear Archivo")
        btn_crear.clicked.connect(self.crear_archivo)
        btn_abrir = QPushButton("Abrir")
        btn_abrir.clicked.connect(self.abrir_archivo)
        btn_modificar = QPushButton("Modificar")
        btn_modificar.clicked.connect(self.modificar_archivo)
        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.clicked.connect(self.eliminar_archivo)
        btn_permisos = QPushButton("Permisos")
        btn_permisos.clicked.connect(self.gestionar_permisos)
        botones_archivos.addWidget(btn_crear)
        botones_archivos.addWidget(btn_abrir)
        botones_archivos.addWidget(btn_modificar)
        botones_archivos.addWidget(btn_eliminar)
        botones_archivos.addWidget(btn_permisos)
        layout_archivos.addLayout(botones_archivos)
        self.pestanas.addTab(tab_archivos, "Archivos")

        # Tab Papelera
        tab_papelera = QWidget()
        layout_papelera = QVBoxLayout(tab_papelera)
        self.lista_papelera = QListWidget()
        layout_papelera.addWidget(QLabel("<b>Papelera de Reciclaje:</b>"))
        layout_papelera.addWidget(self.lista_papelera)
        btn_recuperar = QPushButton("Recuperar")
        btn_recuperar.clicked.connect(self.recuperar_archivo)
        layout_papelera.addWidget(btn_recuperar)
        self.pestanas.addTab(tab_papelera, "Papelera")

        layout_principal.addWidget(self.pestanas)
        self.actualizar_listas()

    def cambiar_usuario(self, nuevo_usuario):
        self.sistema.usuario_actual = nuevo_usuario
        self.label_usuario.setText(f"Usuario actual: <b>{nuevo_usuario}</b>")
        self.actualizar_listas()

    def actualizar_listas(self):
        self.lista_archivos.clear()
        archivos = self.sistema.listar_archivos(False)
        for archivo in archivos:
            self.lista_archivos.addItem(archivo['nombre'])
        self.lista_papelera.clear()
        papelera = self.sistema.listar_archivos(True)
        for archivo in papelera:
            if archivo.get('papelera', False):
                self.lista_papelera.addItem(archivo['nombre'])


    def crear_archivo(self):
        dialogo = DialogoCrearArchivo(self)
        if dialogo.exec():
            nombre, contenido = dialogo.obtener_datos()
            if not nombre:
                QMessageBox.warning(self, "Error", "Debes ingresar un nombre")
                return
            exito, mensaje = self.sistema.crear_archivo(nombre, contenido, self.sistema.usuario_actual)
            if exito:
                QMessageBox.information(self, "Éxito", mensaje)
                self.actualizar_listas()
            else:
                QMessageBox.warning(self, "Error", mensaje)

    def abrir_archivo(self):
        item = self.lista_archivos.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Selecciona un archivo")
            return
        nombre = item.text()
        contenido = self.sistema.leer_contenido(nombre, self.sistema.usuario_actual)
        if contenido is None:
            QMessageBox.warning(self, "Error", "No tienes permiso de lectura")
            return
        archivo = self.sistema.obtener_archivo(nombre)
        dialogo = DialogoVerArchivo(archivo, contenido, self)
        dialogo.exec()

    def modificar_archivo(self):
        item = self.lista_archivos.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Selecciona un archivo")
            return
        nombre = item.text()
        if not self.sistema.verificar_permiso(nombre, self.sistema.usuario_actual, "escritura"):
            QMessageBox.warning(self, "Error", "No tienes permiso de escritura")
            return
        contenido_actual = self.sistema.leer_contenido(nombre, self.sistema.usuario_actual)
        dialogo = DialogoModificarArchivo(nombre, contenido_actual, self)
        if dialogo.exec():
            nuevo_contenido = dialogo.obtener_contenido()
            exito, mensaje = self.sistema.modificar_archivo(nombre, nuevo_contenido, self.sistema.usuario_actual)
            if exito:
                QMessageBox.information(self, "Éxito", mensaje)
                self.actualizar_listas()
            else:
                QMessageBox.warning(self, "Error", mensaje)

    def eliminar_archivo(self):
        item = self.lista_archivos.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Selecciona un archivo")
            return
        nombre = item.text()
        archivo = self.sistema.obtener_archivo(nombre)
        if archivo['propietario'] != self.sistema.usuario_actual and self.sistema.usuario_actual != "admin":
            QMessageBox.warning(self, "Error", "Solo el propietario puede eliminar")
            return
        respuesta = QMessageBox.question(self, "Confirmar", f"¿Eliminar '{nombre}'?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if respuesta == QMessageBox.StandardButton.Yes:
            exito, mensaje = self.sistema.eliminar_archivo(nombre)
            if exito:
                QMessageBox.information(self, "Éxito", mensaje)
                self.actualizar_listas()
            else:
                QMessageBox.warning(self, "Error", mensaje)

    def recuperar_archivo(self):
        item = self.lista_papelera.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Selecciona un archivo de la papelera")
            return
        nombre = item.text()
        exito, mensaje = self.sistema.recuperar_archivo(nombre)
        if exito:
            QMessageBox.information(self, "Éxito", mensaje)
            self.lista_papelera.clearSelection()  # limpiar selección
            self.actualizar_listas()
        else:
            QMessageBox.warning(self, "Error", mensaje)

    def gestionar_permisos(self):
        item = self.lista_archivos.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Selecciona un archivo")
            return
        nombre = item.text()
        archivo = self.sistema.obtener_archivo(nombre)
        if archivo['propietario'] != self.sistema.usuario_actual:
            QMessageBox.warning(self, "Error", "Solo el propietario puede gestionar permisos")
            return
        if self.sistema.usuario_actual != "admin":
            QMessageBox.warning(self, "Error", "Solo el usuario admin puede asignar permisos")
            return
        dialogo = DialogoPermisos(nombre, self.sistema.usuarios)
        if dialogo.exec():
            usuario, lectura, escritura = dialogo.obtener_datos()
            if not usuario:
                QMessageBox.warning(self, "Error", "Debes seleccionar un usuario")
                return
            if self.sistema.asignar_permisos(nombre, usuario, lectura, escritura):
                QMessageBox.information(self, "Éxito", "Permisos asignados correctamente")
            else:
                QMessageBox.warning(self, "Error", "No se pudieron asignar los permisos")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())
