# Alpphas Update

Sistema desktop desenvolvido para gerenciar **clientes, equipamentos, aplicativos e atualizações via ADB** em dispositivos Solinftec.  
Construído em **Python + PySide6**, com banco de dados **MySQL local** e suporte a criação de instalador corporativo.

---

## ✨ Funcionalidades

- 📁 Gerenciamento de Clientes  
- 🔧 Cadastro e vinculação de Equipamentos  
- 📦 Gestão de Aplicativos e versões  
- 🔄 Atualizações via ADB (cadastros, mapas, ponto fixo e aplicativos)  
- 📝 Histórico completo de ações  
- 🖥️ Interface moderna em PySide6  
- 🗄️ Banco local MySQL totalmente automatizado  

---

## 🧩 Arquitetura

```
AlpphasUpdate/
│
├── alpphas_update/
│   ├── src/
│   │   ├── main.py
│   │   ├── db.py
│   │   ├── clientes_window.py
│   │   ├── equipamentos_window.py
│   │   ├── aplicativos_window.py
│   │   ├── atualizacoes_window.py
│   │   ├── adb/
│   │   └── style.py
│   │
│   ├── .env              → Variáveis utilizadas em desenvolvimento
│   ├── venv/             → Ambiente virtual Python
│
├── installer_payload/    → Arquivos usados no instalador NSIS
│   ├── AlpphasUpdate/
│   │   ├── AlpphasUpdate.exe
│   │   ├── .env.prod
│   │   └── adb/
│   │
│   └── mysql/
│       ├── bin/          → MySQL portátil
│       ├── data/         → Diretório inicial do servidor
│       ├── my.ini        → Configuração
│       └── init.sql      → Script que cria banco + usuário + tabelas
│
├── build_release.bat     → Script que gera o .exe de produção
├── AlpphasUpdateInstaller.nsi → Script NSIS do instalador
├── requirements.txt
└── README.md
```

---

## ⚙️ Tecnologias Utilizadas

- Python 3.12  
- PySide6  
- PyInstaller  
- MySQL Portable  
- ADB (Android Debug Bridge)  
- NSIS Installer  

---

## 🚀 Como Executar em Desenvolvimento

1. Ative a venv:
   ```
   .\alpphas_update\venv\Scripts\activate
   ```

2. Instale dependências:
   ```
   pip install -r requirements.txt
   ```

3. Execute a aplicação:
   ```
   python alpphas_update/src/main.py
   ```

---

## 🛠 Processo de Build (Gerar o .exe)

Execute:

```
build_release.bat
```

Esse script:

- Ativa o ambiente virtual  
- Substitui o `.env` pelo `.env.prod`  
- Gera o executável via PyInstaller  
- Restaura o `.env.dev`  

O resultado final ficará em:

```
dist/AlpphasUpdate/AlpphasUpdate.exe
```

---

## 📦 Gerando o Instalador (Setup)

1. Abra o arquivo `AlpphasUpdateInstaller.nsi` no NSIS  
2. Clique em **Compile**  

Será gerado:

```
AlpphasUpdate-Setup-1.0.0.exe
```

Esse instalador contém:

- Aplicação pronta  
- Banco MySQL local  
- Serviço `AlpphasUpdateMySQL`  
- Execução automática do `init.sql`  
- Atalhos no desktop e menu iniciar  

---

## 🧪 Após a Instalação

Configurações do banco:

```
Host: 127.0.0.1
Porta: 3307
Usuário: alpphas_user
Senha: Alpphas@2025
Banco: alpphas_update
```

Verificar serviço:

```
sc query AlpphasUpdateMySQL
```

---

## 💻 Distribuição

Para distribuir internamente:

1. Gere o instalador:  
   ```
   AlpphasUpdate-Setup-1.0.0.exe
   ```
2. Envie para qualquer colaborador  
3. Executar como Administrador  

Não é necessário instalar Python, MySQL ou qualquer outro pacote.

---

## 📄 Licença
Uso interno – Solinftec.  
Distribuição externa proibida.

---

## 👨‍💼 Autor

**João Antonio Diniz Filho**  
Desenvolvedor & Analista de Sucesso do Cliente SR  
Solinftec – 2025
