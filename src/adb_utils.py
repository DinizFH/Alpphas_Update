import os
import shutil
import subprocess
from typing import List, Tuple

# ============================================================
# CONFIGURAÇÃO DO ADB
# ============================================================
# Opções de uso:
#
# 1) Caminho completo para o adb.exe:
#    Ex.: ADB_BIN = r"C:\platform-tools\adb.exe"
#
# 2) Deixar como "adb" e garantir que o adb esteja no PATH
#    do Windows (cmd: adb devices precisa funcionar).
#
# 3) Definir a variável de ambiente ALPPHAS_ADB com o caminho
#    completo para o adb.exe (tem prioridade sobre ADB_BIN).
#
ADB_BIN = r"C:\platform-tools\adb.exe"  # ajuste se o caminho for diferente


def _resolver_caminho_adb() -> str:
    """
    Tenta resolver o caminho do executável ADB, seguindo esta ordem:
    1) Variável de ambiente ALPPHAS_ADB
    2) Caminho absoluto definido em ADB_BIN (se existir)
    3) 'adb' encontrado no PATH do sistema (shutil.which)
    4) Alguns caminhos comuns no Windows (best effort)
    Retorna string vazia ("") se não encontrar.
    """
    # 1) Variável de ambiente
    env_adb = os.getenv("ALPPHAS_ADB")
    if env_adb and os.path.exists(env_adb):
        return env_adb

    # 2) Caminho absoluto configurado em ADB_BIN
    if os.path.isabs(ADB_BIN) and os.path.exists(ADB_BIN):
        return ADB_BIN

    # 3) Procurar no PATH do sistema
    found = shutil.which(ADB_BIN)
    if found:
        return found

    # 4) Alguns caminhos comuns (ajuste se precisar)
    candidatos = [
        r"C:\platform-tools\adb.exe",
        r"C:\Android\platform-tools\adb.exe",
        r"C:\Program Files (x86)\Android\android-sdk\platform-tools\adb.exe",
        r"C:\Program Files\Android\android-sdk\platform-tools\adb.exe",
    ]

    for caminho in candidatos:
        if os.path.exists(caminho):
            return caminho

    return ""


def run_adb(args: List[str]) -> Tuple[bool, str]:
    """
    Executa um comando ADB e retorna (sucesso, log_texto).
    Se o ADB não for encontrado, retorna False com mensagem
    explicando o problema.
    """
    adb_path = _resolver_caminho_adb()

    if not adb_path:
        log = (
            "$ adb " + " ".join(args) + "\n"
            "  [ERRO AO EXECUTAR]: ADB não encontrado.\n"
            "  Verifique se o 'adb.exe' está instalado e:\n"
            "    - Configure o caminho completo em ADB_BIN em adb_utils.py, OU\n"
            "    - Adicione o adb ao PATH do Windows, OU\n"
            "    - Defina a variável de ambiente ALPPHAS_ADB com o caminho do adb.exe.\n"
        )
        return False, log

    cmd = [adb_path] + args

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
        ok = result.returncode == 0

        log = (
            f"$ {' '.join(cmd)}\n"
            f"  -> returncode: {result.returncode}\n"
        )

        if result.stdout:
            log += f"  [stdout]\n{result.stdout}\n"
        if result.stderr:
            log += f"  [stderr]\n{result.stderr}\n"

        return ok, log

    except Exception as e:
        log = (
            f"$ {' '.join(cmd)}\n"
            f"  [ERRO AO EXECUTAR]: {e}\n"
        )
        return False, log


# ============================================================
# DETECÇÃO DO PACOTE SOLINFTEC
# ============================================================

def descobrir_pacote_solinftec() -> str:
    """
    Identifica automaticamente qual app principal da Solinftec
    deve ser limpo antes da atualização.

    Regras:
      1) Procurar pacotes que contenham 's7config' (mais importante)
      2) Se não existir, procurar outros 'com.solinftec.*'
         ignorando 'launcher' e 'speechtotext'
      3) Se ainda assim não achar, retorna string vazia.
    """
    adb_path = _resolver_caminho_adb()
    if not adb_path:
        return ""

    try:
        result = subprocess.run(
            [adb_path, "shell", "pm", "list", "packages"],
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception:
        return ""

    if result.returncode != 0:
        return ""

    pacotes_solinf: List[str] = []
    for linha in result.stdout.splitlines():
        linha = linha.strip()
        if "com.solinftec" in linha:
            # formato: "package:com.solinftec.algumaCoisa"
            pacote = linha.replace("package:", "").strip()
            pacotes_solinf.append(pacote)

    if not pacotes_solinf:
        return ""

    # 1) Prioriza pacotes tipo "s7config"
    for p in pacotes_solinf:
        if "s7config" in p.lower():
            return p

    # 2) Fallback: qualquer outro com.solinftec.*, exceto launcher e speechtotext
    candidatos = [
        p for p in pacotes_solinf
        if "launcher" not in p.lower() and "speechtotext" not in p.lower()
    ]
    if candidatos:
        return candidatos[0]

    # 3) Nada adequado encontrado
    return ""


# ============================================================
# FUNÇÕES DE ALTA NÍVEL
# ============================================================

def testar_conexao_dispositivo() -> List[str]:
    """
    Roda 'adb devices' e retorna logs.
    """
    logs: List[str] = []

    ok, log = run_adb(["devices"])
    logs.append(log)

    return logs


# Diretórios padrão no dispositivo
BASE_TRABALHO = "/sdcard/Trabalho"
DIR_CADASTROS = f"{BASE_TRABALHO}/Cadastros"
DIR_MAPAS = f"{BASE_TRABALHO}/Mapas"
DIR_PONTO_FIXO = f"{BASE_TRABALHO}/PontoFixo"


def _steps_preparar_pasta(destino: str) -> List[List[str]]:
    """
    Gera os passos comuns para garantir a estrutura:

    /sdcard/Trabalho/
        Cadastros/
        Mapas/
        PontoFixo/

    - tenta limpar o app principal da Solinftec (pm clear)
    - garante BASE_TRABALHO com mkdir -p
    - remove a subpasta destino com rm -rf
    - recria a subpasta com mkdir -p
    """
    steps: List[List[str]] = []

    pacote = descobrir_pacote_solinftec()
    if pacote:
        steps.append(["shell", "pm", "clear", pacote])
    else:
        # Apenas loga, sem quebrar fluxo
        steps.append(["shell", "echo", "Nenhum pacote Solinftec relevante encontrado - ignorando pm clear"])

    steps += [
        ["shell", "mkdir", "-p", BASE_TRABALHO],
        ["shell", "rm", "-rf", destino],
        ["shell", "mkdir", "-p", destino],
    ]

    return steps


def atualizar_cadastros(path_local: str) -> List[str]:
    """
    Atualiza a pasta de CADASTROS no dispositivo usando path_local.
    Envia apenas o CONTEÚDO da pasta local para:

        /sdcard/Trabalho/Cadastros
    """
    logs: List[str] = []

    # Enviar somente o conteúdo da pasta (usar "/.")
    src = os.path.join(path_local, ".")

    steps = _steps_preparar_pasta(DIR_CADASTROS)
    steps.append(["push", src, DIR_CADASTROS])

    for args in steps:
        ok, log = run_adb(args)
        logs.append(log)
        if not ok:
            break

    return logs


def atualizar_mapas(path_local: str) -> List[str]:
    """
    Atualiza a pasta de MAPAS no dispositivo usando path_local.
    Envia apenas o CONTEÚDO da pasta local para:

        /sdcard/Trabalho/Mapas
    """
    logs: List[str] = []

    src = os.path.join(path_local, ".")

    steps = _steps_preparar_pasta(DIR_MAPAS)
    steps.append(["push", src, DIR_MAPAS])

    for args in steps:
        ok, log = run_adb(args)
        logs.append(log)
        if not ok:
            break

    return logs


def atualizar_ponto_fixo(path_local: str) -> List[str]:
    """
    Atualiza a pasta de PONTO FIXO no dispositivo usando path_local.
    Envia apenas o CONTEÚDO da pasta local para:

        /sdcard/Trabalho/PontoFixo
    """
    logs: List[str] = []

    src = os.path.join(path_local, ".")

    steps = _steps_preparar_pasta(DIR_PONTO_FIXO)
    steps.append(["push", src, DIR_PONTO_FIXO])

    for args in steps:
        ok, log = run_adb(args)
        logs.append(log)
        if not ok:
            break

    return logs


def atualizar_tudo(path_cad: str, path_mapas: str, path_pf: str) -> List[str]:
    """
    Executa atualização completa: cadastros + mapas + ponto fixo,
    sempre respeitando a estrutura:

    /sdcard/Trabalho/
        Cadastros/
        Mapas/
        PontoFixo/
    """
    logs: List[str] = []

    logs.extend(atualizar_cadastros(path_cad))
    logs.extend(atualizar_mapas(path_mapas))
    logs.extend(atualizar_ponto_fixo(path_pf))

    return logs
