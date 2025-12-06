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
    QAbstractItemView,
    QFileDialog,
    QInputDialog,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor

from clientes_repo import listar_clientes
from equipamentos_repo import listar_equipamentos, criar_equipamento, excluir_equipamento


class EquipamentosWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Alpphas Update - Equipamentos")
        self.resize(900, 500)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        titulo = QLabel("🚜 Equipamentos")
        titulo.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        titulo.setObjectName("pageTitle")

        subtitulo = QLabel(
            "Cadastre modelos de equipamentos vinculados aos clientes e defina as pastas de Cadastros, Mapas e Ponto Fixo."
        )
        subtitulo.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        subtitulo.setObjectName("pageSubtitle")

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)

        # Botões
        botoes_layout = QHBoxLayout()
        botoes_layout.setSpacing(8)

        self.btn_novo = QPushButton("Novo equipamento")
        self.btn_novo.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_novo.clicked.connect(self.novo_equipamento)

        self.btn_excluir = QPushButton("Excluir selecionado")
        self.btn_excluir.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_excluir.clicked.connect(self.excluir_selecionado)

        self.btn_atualizar = QPushButton("Atualizar lista")
        self.btn_atualizar.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_atualizar.clicked.connect(self.carregar_equipamentos)

        botoes_layout.addWidget(self.btn_novo)
        botoes_layout.addWidget(self.btn_excluir)
        botoes_layout.addStretch()
        botoes_layout.addWidget(self.btn_atualizar)

        layout.addLayout(botoes_layout)

        # Tabela
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            [
                "ID",
                "Cliente",
                "Modelo",
                "Cadastros",
                "Mapas",
                "Ponto Fixo",
                "Criado em",
            ]
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.table)

        self.carregar_equipamentos()

    def carregar_equipamentos(self):
        try:
            equips = listar_equipamentos()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar equipamentos:\n{e}")
            return

        self.table.setRowCount(0)

        for row_idx, e in enumerate(equips):
            self.table.insertRow(row_idx)

            item_id = QTableWidgetItem(str(e["id"]))
            item_cliente = QTableWidgetItem(e["cliente_nome"])
            item_nome = QTableWidgetItem(e["nome"])
            item_cad = QTableWidgetItem(e["pasta_cadastros"])
            item_map = QTableWidgetItem(e["pasta_mapas"])
            item_pf = QTableWidgetItem(e["pasta_ponto_fixo"])
            item_criado = QTableWidgetItem(str(e["criado_em"]))

            item_id.setTextAlignment(Qt.AlignCenter)

            self.table.setItem(row_idx, 0, item_id)
            self.table.setItem(row_idx, 1, item_cliente)
            self.table.setItem(row_idx, 2, item_nome)
            self.table.setItem(row_idx, 3, item_cad)
            self.table.setItem(row_idx, 4, item_map)
            self.table.setItem(row_idx, 5, item_pf)
            self.table.setItem(row_idx, 6, item_criado)

        self.table.resizeColumnsToContents()

    def novo_equipamento(self):
        # 1) escolhe o cliente
        try:
            clientes = listar_clientes()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar clientes:\n{e}")
            return

        if not clientes:
            QMessageBox.warning(
                self,
                "Atenção",
                "Nenhum cliente cadastrado. Cadastre um cliente antes de criar equipamentos.",
            )
            return

        opcoes = [f"{c['id']} - {c['nome']}" for c in clientes]

        escolha, ok = QInputDialog.getItem(
            self,
            "Cliente",
            "Selecione o cliente:",
            opcoes,
            0,
            False,
        )
        if not ok or not escolha:
            return

        cliente_id = int(escolha.split(" - ", 1)[0])

        # 2) nome do modelo
        nome_modelo, ok = QInputDialog.getText(
            self,
            "Modelo do equipamento",
            "Informe o modelo do equipamento:",
        )
        if not ok or not nome_modelo.strip():
            return
        nome_modelo = nome_modelo.strip()

        # 3) pastas
        pasta_cad = QFileDialog.getExistingDirectory(
            self,
            "Selecione a pasta de CADASTROS",
            "",
        )
        if not pasta_cad:
            return

        pasta_map = QFileDialog.getExistingDirectory(
            self,
            "Selecione a pasta de MAPAS",
            "",
        )
        if not pasta_map:
            return

        pasta_pf = QFileDialog.getExistingDirectory(
            self,
            "Selecione a pasta de PONTO FIXO",
            "",
        )
        if not pasta_pf:
            return

        try:
            criar_equipamento(
                cliente_id=cliente_id,
                nome=nome_modelo,
                pasta_cadastros=pasta_cad,
                pasta_mapas=pasta_map,
                pasta_ponto_fixo=pasta_pf,
            )
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar equipamento:\n{e}")
            return

        QMessageBox.information(
            self,
            "Sucesso",
            f"Equipamento '{nome_modelo}' cadastrado com sucesso.",
        )
        self.carregar_equipamentos()

    def excluir_selecionado(self):
        linha = self.table.currentRow()
        if linha < 0:
            QMessageBox.warning(
                self, "Atenção", "Selecione um equipamento para excluir."
            )
            return

        item_id = self.table.item(linha, 0)
        item_nome = self.table.item(linha, 2)

        if not item_id:
            QMessageBox.warning(
                self, "Atenção", "Não foi possível identificar o equipamento."
            )
            return

        equip_id = int(item_id.text())
        nome = item_nome.text() if item_nome else "?"

        resp = QMessageBox.question(
            self,
            "Confirmar exclusão",
            f"Tem certeza que deseja excluir o equipamento '{nome}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if resp != QMessageBox.Yes:
            return

        try:
            excluir_equipamento(equip_id)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao excluir equipamento:\n{e}")
            return

        QMessageBox.information(self, "Sucesso", f"Equipamento '{nome}' excluído.")
        self.carregar_equipamentos()
