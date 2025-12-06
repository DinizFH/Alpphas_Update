#Estilização global
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
