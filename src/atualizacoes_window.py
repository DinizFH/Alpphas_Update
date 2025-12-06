from typing import List, Dict
import os

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
    QDialog,
    QListWidget,
    QListWidgetItem,
    QAbstractItemView,
    QApplication,
    QProgressDialog,
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QCursor, QTextCursor

from clientes_repo import listar_clientes
from equipamentos_repo import listar_equipamentos
from aplicativos_repo import listar_aplicativos_instalacao
import adb_utils


class SelecaoListaDialog(QDialog):
    """
    Diálogo genérico de seleção múltipla.
    Recebe uma lista de (texto_visivel, valor_associado).
    """

    def __init__(
        self,
        titulo: str,
        mensagem: str,
        itens: List[tuple[str, str]],
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle(titulo)
        self.resize(450, 350)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        lbl_msg = QLabel(mensagem)
        lbl_msg.setWordWrap(True)
        layout.addWidget(lbl_msg)

        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.MultiSelection)

        for texto, valor in itens:
            item = QListWidgetItem(texto)
            item.setData(Qt.UserRole, valor)
            self.list_widget.addItem(item)

        layout.addWidget(self.list_widget)

        botoes = QHBoxLayout()
        botoes.setSpacing(8)

        btn_cancelar = QPushButton("Cancelar")
        btn_ok = QPushButton("OK")

        btn_cancelar.clicked.connect(self.reject)
        btn_ok.clicked.connect(self.accept)

        botoes.addStretch()
        botoes.addWidget(btn_cancelar)
        botoes.addWidget(btn_ok)

        layout.addLayout(botoes)

    def selecionados(self) -> List[str]:
        valores: List[str] = []
        for item in self.list_widget.selectedItems():
            valores.append(item.data(Qt.UserRole))
        return valores


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
        # Linha de seleção (cliente/equipamento/ADB)
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
        # Cards: Dados / Aplicativos
        # ====================
        cards_row = QHBoxLayout()
        cards_row.setSpacing(16)

        card_dados = self._criar_card_dados()
        card_apps = self._criar_card_aplicativos()

        cards_row.addWidget(card_dados, 1)
        cards_row.addWidget(card_apps, 1)

        layout.addLayout(cards_row)

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

    # -------------------------------------------------------
    # Criação dos cards
    # -------------------------------------------------------

    def _criar_card_dados(self) -> QWidget:
        """
        Card para atualização de Cadastros / Mapas / Ponto Fixo / Tudo.
        """
        card = QWidget()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(10)

        header = QHBoxLayout()
        header.setSpacing(8)

        lbl_icon = QLabel("📂")
        lbl_icon.setObjectName("cardIcon")
        lbl_icon.setFixedWidth(24)

        lbl_title = QLabel("Dados (Trabalho)")
        lbl_title.setObjectName("cardTitle")

        header.addWidget(lbl_icon)
        header.addWidget(lbl_title)
        header.addStretch()

        lbl_desc = QLabel(
            "Atualiza as pastas de CADASTROS, MAPAS e PONTO FIXO "
            "no dispositivo conectado."
        )
        lbl_desc.setWordWrap(True        )
        lbl_desc.setObjectName("cardDesc")

        botoes = QHBoxLayout()
        botoes.setSpacing(8)

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

        botoes.addWidget(self.btn_cad)
        botoes.addWidget(self.btn_mapas)
        botoes.addWidget(self.btn_pf)
        botoes.addWidget(self.btn_tudo)

        card_layout.addLayout(header)
        card_layout.addWidget(lbl_desc)
        card_layout.addStretch()
        card_layout.addLayout(botoes)

        return card

    def _criar_card_aplicativos(self) -> QWidget:
        """
        Card para desinstalar/atualizar aplicativos Solinftec.
        """
        card = QWidget()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(10)

        header = QHBoxLayout()
        header.setSpacing(8)

        lbl_icon = QLabel("📲")
        lbl_icon.setObjectName("cardIcon")
        lbl_icon.setFixedWidth(24)

        lbl_title = QLabel("Aplicativos Solinftec")
        lbl_title.setObjectName("cardTitle")

        header.addWidget(lbl_icon)
        header.addWidget(lbl_title)
        header.addStretch()

        lbl_desc = QLabel(
            "Gerencie os aplicativos Solinftec instalados no dispositivo. "
            "Você pode desinstalar manualmente alguns pacotes ou atualizar "
            "os APKs cadastrados no módulo Aplicativos (install -r)."
        )
        lbl_desc.setWordWrap(True)
        lbl_desc.setObjectName("cardDesc")

        botoes = QHBoxLayout()
        botoes.setSpacing(8)

        self.btn_desinstalar_apps = QPushButton("Desinstalar aplicativos…")
        self.btn_desinstalar_apps.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_desinstalar_apps.clicked.connect(
            self.desinstalar_aplicativos_selecionados
        )

        self.btn_atualizar_apps = QPushButton("Atualizar aplicativos…")
        self.btn_atualizar_apps.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_atualizar_apps.clicked.connect(self.executar_atualizacao_aplicativos)

        botoes.addWidget(self.btn_desinstalar_apps)
        botoes.addWidget(self.btn_atualizar_apps)
        botoes.addStretch()

        card_layout.addLayout(header)
        card_layout.addWidget(lbl_desc)
        card_layout.addStretch()
        card_layout.addLayout(botoes)

        return card

    # -------------------------------------------------------
    # Carregamento / seleção
    # -------------------------------------------------------

    def carregar_dados(self):
        """Carrega listas de clientes e equipamentos do banco e atualiza os combos."""
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

    # -------------------------------------------------------
    # Log helper
    # -------------------------------------------------------

    def append_log(self, text: str):
        self.txt_log.append(text)
        self.txt_log.moveCursor(QTextCursor.End)
        self.txt_log.ensureCursorVisible()

    # -------------------------------------------------------
    # Ações ADB - Teste
    # -------------------------------------------------------

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

    # -------------------------------------------------------
    # Ações ADB - Dados (Trabalho)
    # -------------------------------------------------------

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
            f"=== Atualização COMPLETA (dados) para equipamento '{equip['nome']}' ==="
        )
        self.append_log(f"Cadastros: {cad}")
        self.append_log(f"Mapas: {mapas}")
        self.append_log(f"Ponto Fixo: {pf}\n")

        logs = adb_utils.atualizar_tudo(cad, mapas, pf)
        for log in logs:
            self.append_log(log)

        self.append_log("=== Fim atualização TUDO (dados) ===\n")

    # -------------------------------------------------------
    # Ações ADB - Aplicativos
    # -------------------------------------------------------

    def desinstalar_aplicativos_selecionados(self):
        """
        Mostra um diálogo com os pacotes Solinftec / Bordo relevantes
        e desinstala apenas os selecionados.
        """
        apps_cfg = getattr(adb_utils, "APPS_GERENCIAVEIS", None)
        itens: List[tuple[str, str]] = []

        if apps_cfg:
            # modo configurado manualmente
            for app in apps_cfg:
                pacote = app.get("pacote")
                if not pacote:
                    continue
                nome = app.get("nome_exibicao") or pacote
                label = f"{nome} ({pacote})"
                itens.append((label, pacote))
        else:
            # modo automático: detectar pacotes Solinftec/Bordo
            pacotes = adb_utils.detectar_pacotes_solinftec()
            for pkg in pacotes:
                label = f"Pacote detectado: {pkg}"
                itens.append((label, pkg))

        if not itens:
            QMessageBox.information(
                self,
                "Informação",
                "Nenhum aplicativo Solinftec / Bordo detectado para desinstalar.",
            )
            return

        dlg = SelecaoListaDialog(
            "Desinstalar aplicativos",
            "Selecione os aplicativos que deseja desinstalar:",
            itens,
            parent=self,
        )

        if dlg.exec() != QDialog.Accepted:
            return

        selecionados = dlg.selecionados()
        if not selecionados:
            QMessageBox.information(
                self,
                "Informação",
                "Nenhum aplicativo selecionado para desinstalação.",
            )
            return

        self.append_log("=== Desinstalação de aplicativos (selecionados) ===")
        for pacote in selecionados:
            self.append_log(f"--- Desinstalando {pacote} ---")
            ok, log = adb_utils.run_adb(["uninstall", pacote])
            self.append_log(log)

        self.append_log("=== Fim desinstalação de aplicativos (selecionados) ===\n")

    def executar_atualizacao_aplicativos(self):
        """
        Fluxo de atualização dos aplicativos:

        1) Usuário escolhe quais APKs (do módulo Aplicativos) quer instalar
        2) Para cada APK, roda 'adb install -r':
           - se o app já existir, é atualizado
           - se não existir, é instalado do zero
        3) Mostra barra de progresso durante o processo
        """
        # 1) Buscar versões de aplicativos cadastradas no módulo Aplicativos
        try:
            apps = listar_aplicativos_instalacao()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao listar aplicativos:\n{e}")
            self.append_log("Erro ao listar aplicativos; abortando instalação.\n")
            self.append_log("=== Fim atualização de APLICATIVOS ===\n")
            return

        itens: List[tuple[str, str]] = []
        for app in apps:
            caminho = (
                app.get("arquivo_local")
                or app.get("caminho_arquivo")
                or app.get("path")
                or app.get("arquivo")
                or app.get("apk_path")
            )
            if not caminho:
                continue

            nome = (
                app.get("nome")
                or app.get("descricao")
                or os.path.basename(caminho)
            )
            versao = app.get("versao", "?")
            label = f"{nome} - v{versao}"
            itens.append((label, caminho))

        if not itens:
            QMessageBox.information(
                self,
                "Informação",
                "Nenhum APK com caminho válido foi encontrado no módulo Aplicativos.",
            )
            self.append_log(
                "Nenhum APK com caminho válido encontrado no módulo Aplicativos.\n"
            )
            self.append_log("=== Fim atualização de APLICATIVOS ===\n")
            return

        dlg = SelecaoListaDialog(
            "Instalar aplicativos",
            "Selecione os APKs que deseja instalar/atualizar no dispositivo:",
            itens,
            parent=self,
        )

        if dlg.exec() != QDialog.Accepted:
            self.append_log("Instalação de aplicativos cancelada pelo usuário.\n")
            self.append_log("=== Fim atualização de APLICATIVOS ===\n")
            return

        selecionados = dlg.selecionados()
        if not selecionados:
            QMessageBox.information(
                self,
                "Informação",
                "Nenhum APK selecionado para instalação.",
            )
            self.append_log("Nenhum APK selecionado; nada será instalado.\n")
            self.append_log("=== Fim atualização de APLICATIVOS ===\n")
            return

        total = len(selecionados)
        self.append_log("=== Atualização de APLICATIVOS (install -r) ===")
        self.append_log("📦 Instalando/atualizando APKs selecionados:")

        for apk in selecionados:
            self.append_log(f" - {apk}")

        # Barra de progresso
        progress = QProgressDialog(
            "Instalando aplicativos...",
            "Cancelar",
            0,
            total,
            self,
        )
        progress.setWindowTitle("Atualizando aplicativos")
        progress.setWindowModality(Qt.ApplicationModal)
        progress.setMinimumDuration(0)

        # 3) Instalar um por um, atualizando a barra
        for i, apk in enumerate(selecionados, start=1):
            if progress.wasCanceled():
                self.append_log("Instalação cancelada pelo usuário durante o processo.\n")
                break

            nome_apk = os.path.basename(apk)
            progress.setLabelText(f"Instalando {nome_apk} ({i}/{total})")
            progress.setValue(i - 1)
            QApplication.processEvents()

            logs = adb_utils.instalar_aplicativos([apk])
            for log in logs:
                self.append_log(log)

        progress.setValue(total)
        self.append_log("=== Fim atualização de APLICATIVOS ===\n")
