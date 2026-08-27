# -*- coding: utf-8 -*-
"""
Mòdul de neteja de dades.

Elimina duplicats, gestiona valors nuls, corregeix tipus de dades, tracta
valors atípics (outliers) i genera noves característiques per a la modelització.
"""

import pandas as pd
import numpy as np


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Elimina les files duplicades del DataFrame.

    Args:
        df (pd.DataFrame): Dataset original amb possibles duplicats.

    Returns:
        pd.DataFrame: Còpia del dataset sense registres duplicats.
    """
    return df.drop_duplicates().copy()


def drop_empty_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Elimina les columnes completament buides i metadades no rellevants.

    Args:
        df (pd.DataFrame): Dataset amb les columnes originals.

    Returns:
        pd.DataFrame: Dataset filtrat sense columnes buides ni metadades no rellevants.
    """
    df = df.copy()

    # Columnes completament buides
    empty_cols = df.columns[df.isnull().all()].tolist()
    if empty_cols:
        print(f"Columnes eliminades (100% nuls): {empty_cols}")
    df = df.drop(columns=empty_cols)

    # Columnes no rellevants per a l'anàlisi
    columns_to_drop = ["artist_url",  "scraped_from", "scraped_date"]
    existing = [c for c in columns_to_drop if c in df.columns]
    if existing:
        print(f"Columnes eliminades (metadades no rellevants): {existing}")
    df = df.drop(columns=existing)

    return df


def convert_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma les variables de text corresponents a tipus categòric.

    Args:
        df (pd.DataFrame): Dataset original.

    Returns:
        pd.DataFrame: Dataset amb els tipus de dades optimitzats.
    """
    df = df.copy()
    categorical_cols = ["artist_name"]

    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].astype("category")

    return df


def impute_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Imputa valors nuls basant-se en la tipologia de cada variable.

    Args:
        df (pd.DataFrame): Dataset amb valors absents.

    Returns:
        pd.DataFrame: Dataset complet sense valors nuls a les columnes clau.
    """
    df = df.copy()
    numeric_cols = ["age", "listeners", "scrobbles"]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())

    categorical_cols = ["tags", "bio", "top_track", "similar_artists"]

    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].astype("object").fillna("Unknown")

    # Eliminem les files on el nom de l'artista és nul (no aporten valor)
    df = df.dropna(subset=['artist_name'])

    # Convertim top_track a categòrica després d'imputar els nuls
    if 'top_track' in df.columns:
        df['top_track'] = df['top_track'].astype('category')

    return df


def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Genera noves característiques numèriques i categòriques per als models.

    Args:
        df (pd.DataFrame): Dataset netejat bàsic.

    Returns:
        pd.DataFrame: Dataset ampliat amb transformacions logarítmiques i dummies.
    """
    df = df.copy()

    if "listeners" in df.columns:
        df["listeners_log"] = np.log1p(df["listeners"])

    if "scrobbles" in df.columns:
        df["scrobbles_log"] = np.log1p(df["scrobbles"])

    if "listeners" in df.columns:
        df["popular"] = (df["listeners"] > df["listeners"].median()).astype(int)
        df["popularity_level"] = pd.qcut(df["listeners"], q=3, labels=["Baixa", "Mitjana", "Alta"])

    genres = ["rock", "pop",  "electronic", "hip-hop", "metal", "indie"]

    for genre in genres:

        df[f"tag_{genre}"] = (df["tags"].str.contains(genre, case=False, na=False).astype(int))

    tag_columns = [f"tag_{genre}" for genre in genres]
    df["tag_other"] = (df[tag_columns].sum(axis=1) == 0).astype(int)

    return df


def detect_outliers_iqr(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Identifica els valors atípics (outliers) mitjançant el rang interquartílic (IQR).

    Args:
        df (pd.DataFrame): Dataset d'anàlisi.
        column (str): Nom de la columna numèrica a avaluar.

    Returns:
        pd.DataFrame: Subconjunt de files que es consideren outliers.
    """
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    outliers = df[
        (df[column] < lower_bound) |
        (df[column] > upper_bound)
        ]

    return outliers


def handle_outliers(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """
    Aplica una acotació (capping) als valors extrems detectats amb l'IQR.

    Args:
        df (pd.DataFrame): Dataset d'entrada.
        columns (list): Llista de columnes a les quals aplicar la acotació.

    Returns:
        pd.DataFrame: Dataset amb els valors extrems suavitzats.
    """
    df = df.copy()

    for column in columns:
        # Detectem outliers reutilitzant detect_outliers_iqr
        outliers = detect_outliers_iqr(df, column)
        print(f"Outliers capejats a '{column}': {len(outliers)}")

        # Calculem les fites per al capping
        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        df[column] = df[column].clip(lower=lower_bound, upper=upper_bound)

    return df


def perform_cleaning(df: pd.DataFrame) -> pd.DataFrame:
    """
    Executa de forma seqüencial el pipeline complet de neteja de dades.

    Args:
        df (pd.DataFrame): Dataset original brut.

    Returns:
        pd.DataFrame: Dataset netejat i preparat per a l'anàlisi i modelització.
    """
    print("\n--- Iniciant procés de Neteja ---")
    df = remove_duplicates(df)
    df = drop_empty_columns(df)
    df = convert_data_types(df)
    df = impute_missing_values(df)
    df = handle_outliers(df, ['listeners', 'scrobbles'])
    df = create_features(df)
    print(f"Mida del dataset netejat: {df.shape}")
    return df
