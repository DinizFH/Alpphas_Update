from typing import List, Dict

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QMessageBox,
    QTextEdit,
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QCursor, QTextCursor

from clientes_repo import listar_clientes
from equipamentos_repo import listar_equipamentos
import adb_utils


class AtualizacoesWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Alpphas Update - Atualizações")
        self.resize(950, 550)

        self._clientes: List[Dict] = []
        self._equipamentos: List[Dict] = []

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        titulo = QLabel("🔄 Atualizações")
        titulo.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        titulo.setObjectName("pageTitle")

        subtitulo = QLabel(
            "Selecione o cliente e o equipamento para executar as atualizações via ADB."
        )
        subtitulo.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        subtitulo.setObjectName("pageSubtitle")

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)

        # ====================
        # Linha de seleção
        # ====================
        linha_sel = QHBoxLayout()
        linha_sel.setSpacing(8)

        lbl_cliente = QLabel("Cliente:")
        self.combo_cliente = QComboBox()
        self.combo_cliente.setCursor(QCursor(Qt.PointingHandCursor))
        self.combo_cliente.currentIndexChanged.connect(self._on_cliente_changed)

        lbl_equip = QLabel("Equipamento:")
        self.combo_equip = QComboBox()
        self.combo_equip.setCursor(QCursor(Qt.PointingHandCursor))

        self.btn_testar_adb = QPushButton("Testar conexão ADB")
        self.btn_testar_adb.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_testar_adb.clicked.connect(self.testar_adb)

        linha_sel.addWidget(lbl_cliente)
        linha_sel.addWidget(self.combo_cliente, stretch=1)
        linha_sel.addWidget(lbl_equip)
        linha_sel.addWidget(self.combo_equip, stretch=1)
        linha_sel.addStretch()
        linha_sel.addWidget(self.btn_testar_adb)

        layout.addLayout(linha_sel)

        # ====================
        # Linha de ações
        # ====================
        linha_acoes = QHBoxLayout()
        linha_acoes.setSpacing(8)

        self.btn_cad = QPushButton("Atualizar CADASTROS")
        self.btn_cad.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_cad.clicked.connect(self.executar_cadastros)

        self.btn_mapas = QPushButton("Atualizar MAPAS")
        self.btn_mapas.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_mapas.clicked.connect(self.executar_mapas)

        self.btn_pf = QPushButton("Atualizar PONTO FIXO")
        self.btn_pf.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_pf.clicked.connect(self.executar_ponto_fixo)

        self.btn_tudo = QPushButton("Atualizar TUDO")
        self.btn_tudo.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_tudo.clicked.connect(self.executar_tudo)

        linha_acoes.addWidget(self.btn_cad)
        linha_acoes.addWidget(self.btn_mapas)
        linha_acoes.addWidget(self.btn_pf)
        linha_acoes.addWidget(self.btn_tudo)
        linha_acoes.addStretch()

        layout.addLayout(linha_acoes)

        # ====================
        # Log
        # ====================
        lbl_log = QLabel("Log de execução:")
        layout.addWidget(lbl_log)

        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setMinimumHeight(320)
        layout.addWidget(self.txt_log)

        # Carregar dados iniciais
        self.carregar_dados()

    # ===========================
    # Carregamento / seleção
    # ===========================

    def carregar_dados(self):
        """Carrega listas de clientes e equipamentos do banco e
        atualiza os combos."""
        try:
            self._clientes = listar_clientes()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar clientes:\n{e}")
            self._clientes = []

        try:
            self._equipamentos = listar_equipamentos()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar equipamentos:\n{e}")
            self._equipamentos = []

        # Preenche combo de clientes
        self.combo_cliente.blockSignals(True)
        self.combo_cliente.clear()
        for c in self._clientes:
            self.combo_cliente.addItem(c["nome"], userData=c["id"])
        self.combo_cliente.blockSignals(False)

        self._atualizar_combo_equipamentos()

    def _on_cliente_changed(self):
        self._atualizar_combo_equipamentos()

    def _atualizar_combo_equipamentos(self):
        self.combo_equip.clear()

        if not self._clientes or not self._equipamentos:
            return

        cliente_id = self.combo_cliente.currentData()
        equips_filtrados = [
            e for e in self._equipamentos if e["cliente_id"] == cliente_id
        ]

        for e in equips_filtrados:
            label = f"{e['id']} - {e['nome']}"
            self.combo_equip.addItem(label, userData=e["id"])

    def _equipamento_selecionado(self) -> Dict | None:
        equip_id = self.combo_equip.currentData()
        if equip_id is None:
            return None

        for e in self._equipamentos:
            if e["id"] == equip_id:
                return e
        return None

    @Slot()
    def recarregar_listas(self) -> None:
        """
        Slot para ser conectado aos sinais das telas de Clientes/Equipamentos.
        Recarrega clientes e equipamentos mantendo, se possível,
        o cliente e o equipamento atualmente selecionados.
        """
        cliente_id_atual = self.combo_cliente.currentData()
        equip_id_atual = self.combo_equip.currentData()

        # Recarrega tudo do banco
        self.carregar_dados()

        # Tenta restaurar cliente selecionado
        if cliente_id_atual is not None:
            idx_cli = self.combo_cliente.findData(cliente_id_atual)
            if idx_cli != -1:
                self.combo_cliente.setCurrentIndex(idx_cli)

        # Atualiza equipamentos para o cliente atual
        self._atualizar_combo_equipamentos()

        # Tenta restaurar equipamento selecionado
        if equip_id_atual is not None:
            idx_eq = self.combo_equip.findData(equip_id_atual)
            if idx_eq != -1:
                self.combo_equip.setCurrentIndex(idx_eq)

    # ===========================
    # Log helper
    # ===========================

    def append_log(self, text: str):
        self.txt_log.append(text)
        self.txt_log.moveCursor(QTextCursor.End)
        self.txt_log.ensureCursorVisible()

    # ===========================
    # Ações
    # ===========================

    def testar_adb(self):
        self.append_log("=== Testando conexão ADB ===")
        logs = adb_utils.testar_conexao_dispositivo()
        for log in logs:
            self.append_log(log)
        self.append_log("=== Fim teste ADB ===\n")

    def _validar_equipamento_para_execucao(self) -> Dict | None:
        equip = self._equipamento_selecionado()
        if not equip:
            QMessageBox.warning(
                self,
                "Atenção",
                "Selecione um cliente e um equipamento antes de executar.",
            )
            return None
        return equip

    def executar_cadastros(self):
        equip = self._validar_equipamento_para_execucao()
        if not equip:
            return

        path_cad = equip["pasta_cadastros"]
        self.append_log(
            f"=== Atualizando CADASTROS para equipamento '{equip['nome']}' ==="
        )
        self.append_log(f"Origem local: {path_cad}\n")

        logs = adb_utils.atualizar_cadastros(path_cad)
        for log in logs:
            self.append_log(log)

        self.append_log("=== Fim atualização CADASTROS ===\n")

    def executar_mapas(self):
        equip = self._validar_equipamento_para_execucao()
        if not equip:
            return

        path_mapas = equip["pasta_mapas"]
        self.append_log(
            f"=== Atualizando MAPAS para equipamento '{equip['nome']}' ==="
        )
        self.append_log(f"Origem local: {path_mapas}\n")

        logs = adb_utils.atualizar_mapas(path_mapas)
        for log in logs:
            self.append_log(log)

        self.append_log("=== Fim atualização MAPAS ===\n")

    def executar_ponto_fixo(self):
        equip = self._validar_equipamento_para_execucao()
        if not equip:
            return

        path_pf = equip["pasta_ponto_fixo"]
        self.append_log(
            f"=== Atualizando PONTO FIXO para equipamento '{equip['nome']}' ==="
        )
        self.append_log(f"Origem local: {path_pf}\n")

        logs = adb_utils.atualizar_ponto_fixo(path_pf)
        for log in logs:
            self.append_log(log)

        self.append_log("=== Fim atualização PONTO FIXO ===\n")

    def executar_tudo(self):
        equip = self._validar_equipamento_para_execucao()
        if not equip:
            return

        cad = equip["pasta_cadastros"]
        mapas = equip["pasta_mapas"]
        pf = equip["pasta_ponto_fixo"]

        self.append_log(
            f"=== Atualização COMPLETA para equipamento '{equip['nome']}' ==="
        )
        self.append_log(f"Cadastros: {cad}")
        self.append_log(f"Mapas: {mapas}")
        self.append_log(f"Ponto Fixo: {pf}\n")

        logs = adb_utils.atualizar_tudo(cad, mapas, pf)
        for log in logs:
            self.append_log(log)

        self.append_log("=== Fim atualização TUDO ===\n")
