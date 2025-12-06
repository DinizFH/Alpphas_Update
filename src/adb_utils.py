import subprocess
from typing import List, Tuple


# Se quiser apontar para um adb específico, coloque o caminho completo aqui.
# Ex.: ADB_BIN = r"D:\Android\platform-tools\adb.exe"
ADB_BIN = "adb"


def run_adb(args: List[str]) -> Tuple[bool, str]:
    """
    Executa um comando ADB e retorna (sucesso, log_texto).
    """
    cmd = [ADB_BIN] + args
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
        ok = result.returncode == 0
        log = f"$ {' '.join(cmd)}\n" \
              f"  -> returncode: {result.returncode}\n"

        if result.stdout:
            log += f"  [stdout]\n{result.stdout}\n"
        if result.stderr:
            log += f"  [stderr]\n{result.stderr}\n"

        return ok, log
    except Exception as e:
        return False, f"$ {' '.join(cmd)}\n  [ERRO AO EXECUTAR]: {e}\n"


def testar_conexao_dispositivo() -> List[str]:
    """
    Roda 'adb devices' e retorna logs.
    """
    logs: List[str] = []

    ok, log = run_adb(["devices"])
    logs.append(log)

    return logs


def atualizar_cadastros(path_local: str) -> List[str]:
    """
    Atualiza a pasta de CADASTROS no dispositivo usando o path_local.
    Segue a mesma ideia do .bat:
      - limpa cache do app
      - apaga /sdcard/Trabalho/Cadastros
      - recria diretório
      - faz push dos arquivos locais
    """
    logs: List[str] = []

    steps = [
        ["shell", "pm", "clear", "com.solinftec.s7auxbordo"],
        ["shell", "rm", "-r", "/sdcard/Trabalho/Cadastros"],
        ["shell", "mkdir", "/sdcard/Trabalho/Cadastros"],
        ["push", path_local, "/sdcard/Trabalho/Cadastros"],
    ]

    for args in steps:
        ok, log = run_adb(args)
        logs.append(log)
        if not ok:
            break

    return logs


def atualizar_mapas(path_local: str) -> List[str]:
    logs: List[str] = []

    steps = [
        ["shell", "pm", "clear", "com.solinftec.s7auxbordo"],
        ["shell", "rm", "-r", "/sdcard/Trabalho/Mapas"],
        ["shell", "mkdir", "/sdcard/Trabalho/Mapas"],
        ["push", path_local, "/sdcard/Trabalho/Mapas"],
    ]

    for args in steps:
        ok, log = run_adb(args)
        logs.append(log)
        if not ok:
            break

    return logs


def atualizar_ponto_fixo(path_local: str) -> List[str]:
    logs: List[str] = []

    steps = [
        ["shell", "pm", "clear", "com.solinftec.s7auxbordo"],
        ["shell", "rm", "-r", "/sdcard/Trabalho/PontoFixo"],
        ["shell", "mkdir", "/sdcard/Trabalho/PontoFixo"],
        ["push", path_local, "/sdcard/Trabalho/PontoFixo"],
    ]

    for args in steps:
        ok, log = run_adb(args)
        logs.append(log)
        if not ok:
            break

    return logs


def atualizar_tudo(path_cad: str, path_mapas: str, path_pf: str) -> List[str]:
    """
    Executa atualização completa: cadastros + mapas + ponto fixo.
    """
    logs: List[str] = []

    logs.extend(atualizar_cadastros(path_cad))
    logs.extend(atualizar_mapas(path_mapas))
    logs.extend(atualizar_ponto_fixo(path_pf))

    return logs
