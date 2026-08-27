# -*- coding: utf-8 -*-
"""
Mòdul d'anàlisi estadístic inferencial.

Executa proves d'hipòtesis per avaluar distribucions de variables, normalitat,
homoscedasticitat i correlacions no paramètriques entre indicadors.
"""

from typing import Dict, Any
import pandas as pd
from scipy.stats import pearsonr, spearmanr, kstest, mannwhitneyu, levene


def perform_statistical_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Executa les proves estadístiques i matemàtiques requerides sobre les dades.

    Args:
        df (pd.DataFrame): Dataset netejat d'anàlisi.

    Returns:
        Dict[str, Any]: Resultats estructurats dels p-valors i conclusions de les proves.
    """
    results: Dict[str, Any] = {}

    # Test de Normalitat (Kolmogorov-Smirnov, adequat per a N > 5000)
    # Comprovem si els scrobbles segueixen una distribució normal
    _, p_val = kstest(df['scrobbles'].dropna(), 'norm')
    results['normalitat'] = {
        "variable": "scrobbles",
        "test": "Kolmogorov-Smirnov",
        "p_value": round(p_val, 4),
        "es_normal": p_val > 0.05
    }

    # Correlació
    corr, _ = pearsonr(df['listeners'], df['scrobbles'])
    results['correlacio'] = {
        "listeners_vs_scrobbles": round(corr, 2)
    }

    # Correlació (Spearman, adequada per a dades no normals)
    corr, p_corr = spearmanr(df['listeners'], df['scrobbles'])
    results['correlacio'] = {
        "test": "Spearman",
        "listeners_vs_scrobbles": round(corr, 2),
        "p_value": round(p_corr, 4)
    }

    # Definició de grups per als contrastos
    group_a = df[df['tags'].str.contains('rock', case=False, na=False)]['scrobbles']
    group_b = df[df['tags'].str.contains('pop', case=False, na=False)]['scrobbles']

    # Homocedasticitat (Levene) — Requisit previ al contrast
    _, p_lev = levene(group_a, group_b)
    results['homocedasticitat'] = {
        "comparacio": "Rock vs Pop",
        "test": "Levene",
        "p_value": round(p_lev, 4),
        "variancies_iguals": p_lev > 0.05
    }

    # Contrast d'Hipòtesis (U de Mann-Whitney, no paramètric)
    _, p_mw = mannwhitneyu(group_a, group_b)
    results['contrast_hipotesi'] = {
        "comparacio": "Rock vs Pop",
        "test": "Mann-Whitney U",
        "p_value": round(p_mw, 4),
        "significatiu": p_mw < 0.05
    }

    return results
