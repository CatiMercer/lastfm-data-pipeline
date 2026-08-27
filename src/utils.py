# -*- coding: utf-8 -*-
"""
Mòdul d'utilitats transversals del sistema.

Gestiona els directoris del projecte, l'emmagatzematge dels informes JSON i 
la captura de dades de consola de l'EDA.
"""

import os
import json
import sys
from io import StringIO
from datetime import datetime
from typing import Dict, Any, List, Callable


def ensure_directories(directories: List[str]) -> None:
    """
    Crea les carpetes del sistema sol·licitades si no estan presents al disc.

    Args:
        directories (List[str]): Llista de rutes locals de directoris a assegurar.

    Returns:
        None
    """
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)


def save_report(
        report_data: Dict[str, Any],
        filename: str = None,
        folder: str = "outputs/reports"
    ) -> None:
    """
    Exporta un diccionari estructurat com un fitxer d'informe JSON.

    Args:
        report_data (Dict[str, Any]): Metadades, mètriques o resultats a desar.
        filename (str, opcional): Nom final del fitxer. Si és None, es genera amb timestamp.
        folder (str): Carpeta local on emmagatzemar el JSON (per defecte "outputs/reports").

    Returns:
        None
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{timestamp}.json"

    ensure_directories([folder])
    output_path = os.path.join(folder, filename)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=4, default=str)

    print(f"Informe desat correctament a: {output_path}")


def format_console_header(title: str) -> None:
    """
    Imprimeix un separador gràfic estètic formal per millorar la lectura dels logs de consola.

    Args:
        title (str): Text del títol de l'etapa a emmarcar.

    Returns:
        None
    """
    print("\n" + "="*50)
    print(f" {title.upper()} ".center(50, "="))
    print("="*50)


def generate_eda_log(
        df: Any,
        df_name: str,
        eda_function: Callable[[Any], None],
        filename: str = "eda_log.txt",
        folder: str = "outputs/reports"
    ) -> None:
    """
    Intercepteix la sortida estàndard de la funció d'EDA i la guarda com un fitxer txt formal.

    Args:
        df (Any): Dataset objecte d'avaluació.
        df_name (str): Nom identificador del fitxer original.
        eda_function (Callable): Funció executable que executa l'EDA per consola.
        filename (str): Nom del fitxer log a crear (per defecte "eda_log.txt").
        folder (str): Directori de destinació.

    Returns:
        None
    """
    ensure_directories([folder])

    old_stdout = sys.stdout
    buffer = StringIO()
    sys.stdout = buffer

    try:
        eda_function(df)
    finally:
        sys.stdout = old_stdout

    eda_output = buffer.getvalue()

    line = "=" * 70
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    header = (
        f"{line}\n"
        " INFORME EDA - Pràctica 2: Neteja i Anàlisi de Dades\n"
        f"{line}\n"
        f" Assignatura: Tipologia i Cicle de Vida de les Dades (M2.951)\n"
        f" Autors: Catalina Mª Mercer Campins, Ayany Alvarado Graveran\n"
        f" Data de generació: {timestamp}\n"
        f" Dataset analitzat: {df_name}\n"
        f" Registres: {df.shape[0]} | Variables: {df.shape[1]}\n"
        f"{line}\n\n"
    )

    output_path = os.path.join(folder, filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(header)
        f.write(eda_output)

    print(f"Log EDA generat a: {output_path}")
