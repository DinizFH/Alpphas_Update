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

from aplicativos_repo import (
    listar_aplicativos_resumo,
    criar_aplicativo,
    criar_versao,
    excluir_aplicativo,
)


class AplicativosWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Alpphas Update - Aplicativos")
        self.resize(800, 500)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        titulo = QLabel("📦 Aplicativos")
        titulo.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        titulo.setObjectName("pageTitle")

        subtitulo = QLabel(
            "Gerencie o repositório de aplicativos (APKs) e suas versões."
        )
        subtitulo.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        subtitulo.setObjectName("pageSubtitle")

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)

        # Botões
        botoes_layout = QHBoxLayout()
        botoes_layout.setSpacing(8)

        self.btn_novo = QPushButton("Novo aplicativo (com APK)")
        self.btn_novo.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_novo.clicked.connect(self.novo_aplicativo)

        self.btn_excluir = QPushButton("Excluir selecionado")
        self.btn_excluir.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_excluir.clicked.connect(self.excluir_selecionado)

        self.btn_atualizar = QPushButton("Atualizar lista")
        self.btn_atualizar.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_atualizar.clicked.connect(self.carregar_aplicativos)

        botoes_layout.addWidget(self.btn_novo)
        botoes_layout.addWidget(self.btn_excluir)
        botoes_layout.addStretch()
        botoes_layout.addWidget(self.btn_atualizar)

        layout.addLayout(botoes_layout)

        # Tabela
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Nome", "Total versões", "Última versão", "Criado em"]
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.table)

        self.carregar_aplicativos()

    def carregar_aplicativos(self):
        try:
            apps = listar_aplicativos_resumo()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar aplicativos:\n{e}")
            return

        self.table.setRowCount(0)

        for row_idx, a in enumerate(apps):
            self.table.insertRow(row_idx)

            item_id = QTableWidgetItem(str(a["id"]))
            item_nome = QTableWidgetItem(a["nome"])
            item_total = QTableWidgetItem(str(a["total_versoes"]))
            item_ultima = QTableWidgetItem(a["ultima_versao"] or "-")
            item_criado = QTableWidgetItem(str(a["criado_em"]))

            item_id.setTextAlignment(Qt.AlignCenter)
            item_total.setTextAlignment(Qt.AlignCenter)

            self.table.setItem(row_idx, 0, item_id)
            self.table.setItem(row_idx, 1, item_nome)
            self.table.setItem(row_idx, 2, item_total)
            self.table.setItem(row_idx, 3, item_ultima)
            self.table.setItem(row_idx, 4, item_criado)

        self.table.resizeColumnsToContents()

    def novo_aplicativo(self):
        nome, ok = QInputDialog.getText(
            self,
            "Novo aplicativo",
            "Nome do aplicativo (ex.: S7 TPL, Launcher, ConfigMag):",
        )
        if not ok or not nome.strip():
            return
        nome = nome.strip()

        arquivo, _ = QFileDialog.getOpenFileName(
            self,
            "Selecione o arquivo APK",
            "",
            "Arquivos APK (*.apk)",
        )
        if not arquivo:
            return

        try:
            filename = arquivo.split("/")[-1].split("\\")[-1]
        except Exception:
            filename = ""

        versao, ok = QInputDialog.getText(
            self,
            "Versão",
            "Informe a versão deste APK:",
            text=filename,
        )
        if not ok or not versao.strip():
            return
        versao = versao.strip()

        try:
            app_id = criar_aplicativo(nome)
            criar_versao(app_id, versao, arquivo, padrao=True)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar aplicativo:\n{e}")
            return

        QMessageBox.information(
            self,
            "Sucesso",
            f"Aplicativo '{nome}' cadastrado com versão '{versao}'.",
        )
        self.carregar_aplicativos()

    def excluir_selecionado(self):
        linha = self.table.currentRow()
        if linha < 0:
            QMessageBox.warning(self, "Atenção", "Selecione um aplicativo para excluir.")
            return

        item_id = self.table.item(linha, 0)
        item_nome = self.table.item(linha, 1)

        if not item_id:
            QMessageBox.warning(
                self, "Atenção", "Não foi possível identificar o aplicativo selecionado."
            )
            return

        app_id = int(item_id.text())
        nome = item_nome.text() if item_nome else "?"

        resp = QMessageBox.question(
            self,
            "Confirmar exclusão",
            f"Tem certeza que deseja excluir o aplicativo '{nome}' e todas as suas versões?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if resp != QMessageBox.Yes:
            return

        try:
            excluir_aplicativo(app_id)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao excluir aplicativo:\n{e}")
            return

        QMessageBox.information(self, "Sucesso", f"Aplicativo '{nome}' excluído.")
        self.carregar_aplicativos()
