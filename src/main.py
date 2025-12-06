import sys
import _mysql_connector
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QInputDialog,
    QAbstractItemView,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor

from clientes_repo import listar_clientes, criar_cliente, excluir_cliente


# =======================================
#           JANELA DE CLIENTES
# =======================================
class ClientesWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Alpphas Update - Clientes")
        self.resize(700, 500)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Título
        titulo = QLabel("👤 Clientes")
        titulo.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        titulo.setObjectName("pageTitle")

        subtitulo = QLabel(
            "Cadastre e gerencie os clientes para vincular equipamentos e atualizações."
        )
        subtitulo.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        subtitulo.setObjectName("pageSubtitle")

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)

        # Botões
        botoes_layout = QHBoxLayout()
        botoes_layout.setSpacing(8)

        self.btn_novo = QPushButton("Novo cliente")
        self.btn_novo.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_novo.clicked.connect(self.novo_cliente)

        self.btn_excluir = QPushButton("Excluir selecionado")
        self.btn_excluir.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_excluir.clicked.connect(self.excluir_selecionado)

        self.btn_atualizar = QPushButton("Atualizar lista")
        self.btn_atualizar.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_atualizar.clicked.connect(self.carregar_clientes)

        botoes_layout.addWidget(self.btn_novo)
        botoes_layout.addWidget(self.btn_excluir)
        botoes_layout.addStretch()
        botoes_layout.addWidget(self.btn_atualizar)

        layout.addLayout(botoes_layout)

        # Tabela
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Nome", "Criado em"])

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.table)

        # Carregar dados
        self.carregar_clientes()

    # ======================
    # Funções de interação
    # ======================

    def carregar_clientes(self):
        """
        Busca todos os clientes no banco e atualiza a tabela.
        """
        try:
            clientes = listar_clientes()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar clientes:\n{e}")
            return

        self.table.setRowCount(0)

        for row_idx, c in enumerate(clientes):
            self.table.insertRow(row_idx)

            item_id = QTableWidgetItem(str(c["id"]))
            item_nome = QTableWidgetItem(c["nome"])
            item_criado = QTableWidgetItem(str(c["criado_em"]))

            item_id.setTextAlignment(Qt.AlignCenter)

            self.table.setItem(row_idx, 0, item_id)
            self.table.setItem(row_idx, 1, item_nome)
            self.table.setItem(row_idx, 2, item_criado)

        self.table.resizeColumnsToContents()

    def novo_cliente(self):
        """
        Abre um input para cadastrar um novo cliente (somente nome).
        """
        nome, ok = QInputDialog.getText(
            self,
            "Novo cliente",
            "Nome do cliente:",
        )

        if not ok or not nome.strip():
            return

        nome = nome.strip()

        try:
            novo_id = criar_cliente(nome)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao criar cliente:\n{e}")
            return

        QMessageBox.information(
            self,
            "Sucesso",
            f"Cliente '{nome}' criado com ID {novo_id}.",
        )

        self.carregar_clientes()

    def excluir_selecionado(self):
        """
        Exclui o cliente selecionado na tabela.
        """
        linha = self.table.currentRow()
        if linha < 0:
            QMessageBox.warning(self, "Atenção", "Selecione um cliente para excluir.")
            return

        item_id = self.table.item(linha, 0)
        item_nome = self.table.item(linha, 1)

        if not item_id:
            QMessageBox.warning(
                self, "Atenção", "Não foi possível identificar o cliente selecionado."
            )
            return

        cliente_id = int(item_id.text())
        nome = item_nome.text() if item_nome else "?"

        resp = QMessageBox.question(
            self,
            "Confirmar exclusão",
            f"Tem certeza que deseja excluir o cliente '{nome}' (ID {cliente_id})?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if resp != QMessageBox.Yes:
            return

        try:
            excluir_cliente(cliente_id)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao excluir cliente:\n{e}")
            return

        QMessageBox.information(self, "Sucesso", f"Cliente '{nome}' excluído.")
        self.carregar_clientes()


# =======================================
#           DASHBOARD PRINCIPAL
# =======================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Alpphas Update")
        self.resize(1000, 600)

        self.clientes_window = None  # para manter referência

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
            icone="📦",
            titulo="Aplicativos",
            descricao="Repositório de APKs e versões (em construção).",
            callback=self.nao_implementado,
        )

        row1.addWidget(card_clientes)
        row1.addWidget(card_aplicativos)

        # Linha 2: Equipamentos / Atualizações
        row2 = QHBoxLayout()
        row2.setSpacing(20)

        card_equipamentos = self._criar_card(
            icone="🚜",
            titulo="Equipamentos",
            descricao="Modelos de equipamentos amarrados aos clientes (em construção).",
            callback=self.nao_implementado,
        )

        card_atualizacoes = self._criar_card(
            icone="🔄",
            titulo="Atualizações",
            descricao="Fluxo de atualização via ADB (em construção).",
            callback=self.nao_implementado,
        )

        row2.addWidget(card_equipamentos)
        row2.addWidget(card_atualizacoes)

        layout.addLayout(row1)
        layout.addLayout(row2)
        layout.addStretch()

    def _criar_card(self, icone: str, titulo: str, descricao: str, callback):
        """
        Cria um card clicável com ícone, título, descrição e botão.
        """
        card = QWidget()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(10)

        # Ícone + título
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

    # ===== Ações dos cards =====

    def abrir_clientes(self):
        if self.clientes_window is None:
            self.clientes_window = ClientesWindow()
        self.clientes_window.show()
        self.clientes_window.raise_()
        self.clientes_window.activateWindow()

    def nao_implementado(self):
        QMessageBox.information(
            self,
            "Em construção",
            "Este módulo ainda será implementado.",
        )


# =======================================
#           ESTILO GLOBAL (CSS)
# =======================================
ESTILO_GLOBAL = """
QMainWindow {
    background-color: #020617;
}

QWidget {
    color: #e5e7eb;
    font-family: "Segoe UI", sans-serif;
    font-size: 12px;
}

/* Títulos gerais */
#appTitle {
    font-size: 26px;
    font-weight: 700;
    color: #f9fafb;
}
#appSubtitle {
    font-size: 12px;
    color: #9ca3af;
}

/* Títulos de página (Clientes, etc.) */
#pageTitle {
    font-size: 22px;
    font-weight: 600;
    color: #f9fafb;
}
#pageSubtitle {
    font-size: 11px;
    color: #9ca3af;
}

/* Cards do dashboard */
#card {
    background-color: #0f172a;
    border: 1px solid #1f2937;
    border-radius: 16px;
}
#card:hover {
    border: 1px solid #2563eb;
}

/* Conteúdo dos cards */
#cardIcon {
    font-size: 20px;
}
#cardTitle {
    font-size: 18px;
    font-weight: 600;
}
#cardDesc {
    font-size: 12px;
    color: #9ca3af;
}

/* Botões */
QPushButton {
    background-color: #2563eb;
    color: #e5e7eb;
    border-radius: 8px;
    padding: 6px 16px;
    border: none;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #1d4ed8;
}
QPushButton:pressed {
    background-color: #1e40af;
}

/* Tabela */
QHeaderView::section {
    background-color: #111827;
    color: #e5e7eb;
    padding: 4px;
    border: none;
}
QTableWidget {
    background-color: #020617;
    gridline-color: #1f2937;
    border: 1px solid #1f2937;
}
QTableWidget::item {
    selection-background-color: #1d4ed8;
}
"""


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(ESTILO_GLOBAL)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
