from PySide6.QtWidgets import (
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

    def carregar_clientes(self):
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
