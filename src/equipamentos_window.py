import os
import sys
import subprocess

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
    QComboBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor

from clientes_repo import listar_clientes
from equipamentos_repo import (
    listar_equipamentos,
    criar_equipamento,
    atualizar_equipamento,
    excluir_equipamento,
)


class EquipamentosWindow(QMainWindow):
    # Sinal para avisar outras telas (Atualizações)
    equipamentos_atualizados = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Alpphas Update - Equipamentos")
        self.resize(900, 520)

        # lista completa (para filtro por cliente)
        self._equipamentos_todos = []

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

        # =======================
        # Linha de botões + filtro
        # =======================
        topo_layout = QHBoxLayout()
        topo_layout.setSpacing(8)

        self.btn_novo = QPushButton("Novo equipamento")
        self.btn_novo.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_novo.clicked.connect(self.novo_equipamento)

        self.btn_editar = QPushButton("Editar selecionado")
        self.btn_editar.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_editar.clicked.connect(self.editar_selecionado)

        self.btn_excluir = QPushButton("Excluir selecionado")
        self.btn_excluir.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_excluir.clicked.connect(self.excluir_selecionado)

        topo_layout.addWidget(self.btn_novo)
        topo_layout.addWidget(self.btn_editar)
        topo_layout.addWidget(self.btn_excluir)
        topo_layout.addStretch()

        lbl_filtro = QLabel("Cliente:")
        self.combo_cliente = QComboBox()
        self.combo_cliente.setCursor(QCursor(Qt.PointingHandCursor))
        self.combo_cliente.currentIndexChanged.connect(self.aplicar_filtro_cliente)

        self.btn_atualizar = QPushButton("Atualizar lista")
        self.btn_atualizar.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_atualizar.clicked.connect(self.recarregar_dados)

        topo_layout.addWidget(lbl_filtro)
        topo_layout.addWidget(self.combo_cliente)
        topo_layout.addWidget(self.btn_atualizar)

        layout.addLayout(topo_layout)

        # =======================
        # Linha de botões: abrir pastas
        # =======================
        abrir_layout = QHBoxLayout()
        abrir_layout.setSpacing(8)

        self.btn_abrir_cad = QPushButton("Abrir CADASTROS")
        self.btn_abrir_cad.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_abrir_cad.clicked.connect(lambda: self.abrir_pasta("cad"))

        self.btn_abrir_map = QPushButton("Abrir MAPAS")
        self.btn_abrir_map.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_abrir_map.clicked.connect(lambda: self.abrir_pasta("map"))

        self.btn_abrir_pf = QPushButton("Abrir PONTO FIXO")
        self.btn_abrir_pf.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_abrir_pf.clicked.connect(lambda: self.abrir_pasta("pf"))

        abrir_layout.addWidget(self.btn_abrir_cad)
        abrir_layout.addWidget(self.btn_abrir_map)
        abrir_layout.addWidget(self.btn_abrir_pf)
        abrir_layout.addStretch()

        layout.addLayout(abrir_layout)

        # =======================
        # Tabela
        # =======================
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

        # Carregar dados iniciais
        self.recarregar_dados()

    # ============================
    # Carregamento de dados
    # ============================

    def recarregar_dados(self):
        self.carregar_clientes_filtro()
        self.carregar_equipamentos()

    def carregar_clientes_filtro(self):
        """
        Preenche o combo de filtro de clientes.
        """
        try:
            clientes = listar_clientes()
        except Exception as e:
            QMessageBox.critical(
                self, "Erro", f"Erro ao carregar clientes para filtro:\n{e}"
            )
            return

        self.combo_cliente.blockSignals(True)
        self.combo_cliente.clear()
        self.combo_cliente.addItem("Todos os clientes", userData=None)

        for c in clientes:
            self.combo_cliente.addItem(c["nome"], userData=c["id"])

        self.combo_cliente.blockSignals(False)

    def carregar_equipamentos(self):
        """
        Busca todos os equipamentos e aplica o filtro atual do combo.
        """
        try:
            equips = listar_equipamentos()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar equipamentos:\n{e}")
            return

        self._equipamentos_todos = equips
        self.aplicar_filtro_cliente()

    def aplicar_filtro_cliente(self):
        """
        Aplica filtro de cliente sobre self._equipamentos_todos
        e preenche a tabela.
        """
        cliente_id = self.combo_cliente.currentData()
        equips = self._equipamentos_todos or []

        if cliente_id is not None:
            equips = [e for e in equips if e["cliente_id"] == cliente_id]

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

    # ============================
    # CRUD
    # ============================

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
        self.recarregar_dados()

        # Avisa todo mundo (Atualizações, etc.)
        self.equipamentos_atualizados.emit()

    def editar_selecionado(self):
        linha = self.table.currentRow()
        if linha < 0:
            QMessageBox.warning(
                self, "Atenção", "Selecione um equipamento para editar."
            )
            return

        item_id = self.table.item(linha, 0)
        item_nome = self.table.item(linha, 2)
        item_cad = self.table.item(linha, 3)
        item_map = self.table.item(linha, 4)
        item_pf = self.table.item(linha, 5)

        if not item_id:
            QMessageBox.warning(
                self, "Atenção", "Não foi possível identificar o equipamento."
            )
            return

        equip_id = int(item_id.text())
        nome_atual = item_nome.text() if item_nome else ""
        cad_atual = item_cad.text() if item_cad else ""
        map_atual = item_map.text() if item_map else ""
        pf_atual = item_pf.text() if item_pf else ""

        # Nome
        novo_nome, ok = QInputDialog.getText(
            self,
            "Editar modelo",
            "Modelo do equipamento:",
            text=nome_atual,
        )
        if not ok or not novo_nome.strip():
            return
        novo_nome = novo_nome.strip()

        # Pastas (se cancelar, mantém a atual)
        nova_cad = QFileDialog.getExistingDirectory(
            self,
            "Selecione a pasta de CADASTROS (Cancel = manter atual)",
            cad_atual or "",
        )
        if not nova_cad:
            nova_cad = cad_atual

        nova_map = QFileDialog.getExistingDirectory(
            self,
            "Selecione a pasta de MAPAS (Cancel = manter atual)",
            map_atual or "",
        )
        if not nova_map:
            nova_map = map_atual

        nova_pf = QFileDialog.getExistingDirectory(
            self,
            "Selecione a pasta de PONTO FIXO (Cancel = manter atual)",
            pf_atual or "",
        )
        if not nova_pf:
            nova_pf = pf_atual

        try:
            atualizar_equipamento(
                equipamento_id=equip_id,
                nome=novo_nome,
                pasta_cadastros=nova_cad,
                pasta_mapas=nova_map,
                pasta_ponto_fixo=nova_pf,
            )
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao atualizar equipamento:\n{e}")
            return

        QMessageBox.information(
            self,
            "Sucesso",
            f"Equipamento '{novo_nome}' atualizado com sucesso.",
        )
        self.recarregar_dados()

        # Também dispara, porque Atualizações pode estar aberta
        self.equipamentos_atualizados.emit()

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
        self.recarregar_dados()

        # Emite sinal para atualizar combos em Atualizações
        self.equipamentos_atualizados.emit()

    # ============================
    # Abrir pastas
    # ============================

    def abrir_pasta(self, tipo: str):
        """
        tipo: 'cad', 'map', 'pf'
        """
        linha = self.table.currentRow()
        if linha < 0:
            QMessageBox.warning(
                self, "Atenção", "Selecione um equipamento para abrir a pasta."
            )
            return

        col_map = {"cad": 3, "map": 4, "pf": 5}
        col = col_map.get(tipo)
        if col is None:
            return

        item_path = self.table.item(linha, col)
        path = item_path.text() if item_path else ""

        if not path:
            QMessageBox.warning(self, "Atenção", "Caminho da pasta não encontrado.")
            return

        if not os.path.isdir(path):
            QMessageBox.warning(
                self,
                "Atenção",
                f"A pasta não existe mais no caminho informado:\n{path}",
            )
            return

        try:
            self._abrir_no_explorer(path)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro",
                f"Não foi possível abrir a pasta:\n{path}\n\n{e}",
            )

    @staticmethod
    def _abrir_no_explorer(path: str):
        if sys.platform.startswith("win"):
            os.startfile(path)
        elif sys.platform.startswith("darwin"):
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
