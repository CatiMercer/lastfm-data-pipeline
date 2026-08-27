# -*- coding: utf-8 -*-
"""
Mòdul de càrrega de dades.

Obre els fitxers d'origen CSV i executa el diagnòstic exploratori
inicial per consola (EDA).
"""

import pandas as pd


def load_dataset(file_path: str) -> pd.DataFrame:
    """
    Carrega un fitxer CSV en un DataFrame de Pandas de manera segura.

    Args:
        file_path (str): Ruta local del fitxer a obrir.

    Returns:
        pd.DataFrame: Dataset carregat o un DataFrame buit si falla la lectura.
    """
    # Si es proporciona una ruta invalida, retornem un DataFrame buit.
    if not file_path:
        return pd.DataFrame()

    try:
        # Intentem carregar el fitxer CSV.
        df: pd.DataFrame = pd.read_csv(file_path, encoding='utf-8-sig')
        print(f"Dataset carregat: {df.shape[0]} files x {df.shape[1]} columnes")
        return df

    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR inesperat carregant '{file_path}': {e}")
        return pd.DataFrame()


def perform_eda(df: pd.DataFrame) -> None:
    """
    Mostra per consola l'estructura interna i les estadístiques bàsiques del dataset.

    Args:
        df (pd.DataFrame): Dataset que es vol explorar.

    Returns:
        None
    """
    if df.empty:
        print("El DataFrame està buit.")
        return

    # Mostrem les primeres 5 files.
    print("\n--- 1. Primeres 5 files ---")
    print(df.head())

    # Mostrem les columnes (Noms de les variables).
    print("\n--- 2. Columnes del DataFrame ---")
    print(list(df.columns))

    # Mostrem la informació general del DataFrame.
    print("\n--- 3. Informació General ---")
    df.info()

    # Identificació de dades mancants
    print("\n--- 4. Valors buits per columna ---")
    print(df.isnull().sum())

    # Identificació de zeros que poden indicar pèrdua de dades
    print("\n--- 5. Conteig de valors zero ---")
    print((df.select_dtypes(include='number') == 0).sum())

    print("\n--- 6. Estadístiques descriptives (numèriques) ---")
    print(df.describe())

    print("\n--- 7. Estadístiques descriptives (categòriques) ---")
    print(df.describe(include='object'))
