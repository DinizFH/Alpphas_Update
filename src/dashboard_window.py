from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor

from clientes_window import ClientesWindow
from aplicativos_window import AplicativosWindow
from equipamentos_window import EquipamentosWindow
from atualizacoes_window import AtualizacoesWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Alpphas Update")
        self.resize(1000, 600)

        self.clientes_window = None
        self.aplicativos_window = None
        self.equipamentos_window = None
        self.atualizacoes_window = None

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        titulo = QLabel("Alpphas Update")
        titulo.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        titulo.setObjectName("appTitle")

        subtitulo = QLabel(
            "Gerencie clientes, aplicativos, equipamentos e atualizações em um só lugar."
        )
        subtitulo.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        subtitulo.setObjectName("appSubtitle")

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)

        # Linha 1: Clientes / Aplicativos
        row1 = QHBoxLayout()
        row1.setSpacing(20)

        card_clientes = self._criar_card(
            icone="👤",
            titulo="Clientes",
            descricao="Cadastrar e gerenciar clientes.",
            callback=self.abrir_clientes,
        )

        card_aplicativos = self._criar_card(
            icone="📱",
            titulo="Aplicativos",
            descricao="Repositório de APKs e versões.",
            callback=self.abrir_aplicativos,
        )

        row1.addWidget(card_clientes)
        row1.addWidget(card_aplicativos)

        # Linha 2: Equipamentos / Atualizações
        row2 = QHBoxLayout()
        row2.setSpacing(20)

        card_equipamentos = self._criar_card(
            icone="🚜",
            titulo="Equipamentos",
            descricao="Modelos de equipamentos amarrados aos clientes.",
            callback=self.abrir_equipamentos,
        )

        card_atualizacoes = self._criar_card(
            icone="🔄",
            titulo="Atualizações",
            descricao="Fluxo de atualizações via ADB.",
            callback=self.abrir_atualizacoes,
        )

        row2.addWidget(card_equipamentos)
        row2.addWidget(card_atualizacoes)

        layout.addLayout(row1)
        layout.addLayout(row2)
        layout.addStretch()

    def _criar_card(self, icone: str, titulo: str, descricao: str, callback):
        card = QWidget()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(10)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        lbl_icone = QLabel(icone)
        lbl_icone.setObjectName("cardIcon")
        lbl_icone.setFixedWidth(28)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setObjectName("cardTitle")

        header_layout.addWidget(lbl_icone)
        header_layout.addWidget(lbl_titulo)
        header_layout.addStretch()

        lbl_desc = QLabel(descricao)
        lbl_desc.setObjectName("cardDesc")
        lbl_desc.setWordWrap(True)

        btn = QPushButton("Abrir")
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.clicked.connect(callback)
        btn.setObjectName("cardButton")

        card_layout.addLayout(header_layout)
        card_layout.addWidget(lbl_desc)
        card_layout.addStretch()
        card_layout.addWidget(btn, alignment=Qt.AlignRight)

        return card

    def abrir_clientes(self):
        if self.clientes_window is None:
            self.clientes_window = ClientesWindow()
        self.clientes_window.show()
        self.clientes_window.raise_()
        self.clientes_window.activateWindow()

    def abrir_aplicativos(self):
        if self.aplicativos_window is None:
            self.aplicativos_window = AplicativosWindow()
        self.aplicativos_window.show()
        self.aplicativos_window.raise_()
        self.aplicativos_window.activateWindow()

    def abrir_equipamentos(self):
        if self.equipamentos_window is None:
            self.equipamentos_window = EquipamentosWindow()
        self.equipamentos_window.show()
        self.equipamentos_window.raise_()
        self.equipamentos_window.activateWindow()

    def abrir_atualizacoes(self):
        if self.atualizacoes_window is None:
            self.atualizacoes_window = AtualizacoesWindow()
        self.atualizacoes_window.show()
        self.atualizacoes_window.raise_()
        self.atualizacoes_window.activateWindow()
