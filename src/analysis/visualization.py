# -*- coding: utf-8 -*-
"""
Mòdul de visualització gràfica.

Genera i exporta diagrames de caixa, histogrames, diagrames de violí, mapes de
calor de correlació i gràfics de dispersió.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


COLUMN_LABELS: dict = {
    "listeners": "nombre d'oients (listeners)",
    "listeners_log": "listeners (escala logarítmica)",
    "scrobbles": "nombre de reproduccions (scrobbles)",
    "scrobbles_log": "scrobbles (escala logarítmica)",
    "popular": "variable objectiu (popular)",
    "popularity_level": "nivells de popularitat dels artistes"
}

AXIS_LABELS: dict = {
    "listeners": "Nombre d'oients",
    "listeners_log": "Oients (log)",
    "scrobbles": "Nombre de reproduccions",
    "scrobbles_log": "Reproduccions (log)",
    "popular": "Popularitat",
    "popularity_level": "Nivell de popularitat"
}


def save_plot(fig: plt.Figure, filename: str, path: str = "outputs/img") -> None:
    """
    Desa de forma física al disc la figura de Matplotlib en format PNG.

    Args:
        fig (plt.Figure): Instància del gràfic actiu de Matplotlib.
        filename (str): Nom final del fitxer de sortida.
        path (str): Carpeta local on emmagatzemar la imatge (per defecte "outputs/img").

    Returns:
        None
    """
    # Crear carpeta si no existeix
    os.makedirs(path, exist_ok=True)

    # Desem la figura.
    output_path = os.path.join(path, filename)
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)


def plot_distribution(df: pd.DataFrame, column: str, path: str = "outputs/img") -> None:
    """
    Dibuixa l'histograma juntament amb la línia de densitat estimada (KDE).

    Args:
        df (pd.DataFrame): Dataset d'anàlisi.
        column (str): Nom de la columna de dades continuas a dibuixar.
        path (str): Carpeta de sortida del fitxer generat.

    Returns:
        None
    """
    title = f"Distribució del {COLUMN_LABELS.get(column, column)}"

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(data=df, x=column, bins=50, kde=True, ax=ax)
    ax.set_title(title)
    ax.set_xlabel(AXIS_LABELS.get(column, column))
    ax.set_ylabel("Freqüència")
    save_plot(fig, f"distribution_{column}.png", path)


def plot_categorical_distribution(
        df: pd.DataFrame,
        column: str,
        path: str = "outputs/img"
    ) -> None:
    """
    Genera un gràfic de barres de recompte de freqüències per a dades categòriques.

    Args:
        df (pd.DataFrame): Dataset d'anàlisi.
        column (str): Nom del factor categòric a avaluar.
        path (str): Directori de sortida.

    Returns:
        None
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.countplot(data=df,  x=column, ax=ax)
    title = f"Distribució del {COLUMN_LABELS.get(column, column)}"
    ax.set_title(title)
    ax.set_xlabel(AXIS_LABELS.get(column, column))
    ax.set_ylabel("Freqüència")
    save_plot(fig, f"categorical_distribution_{column}.png", path)


def plot_boxplot(df: pd.DataFrame, column: str, path: str = "outputs/img") -> None:
    """
    Dibuixa un diagrama de caixes per analitzar gràficament la dispersió i outliers.

    Args:
        df (pd.DataFrame): Dataset d'anàlisi.
        column (str): Variable contínua que es vol graficar.
        path (str): Directori on exportar el gràfic.

    Returns:
        None
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(data=df, x=column, ax=ax)
    title = f"Distribució i valors extrems de {COLUMN_LABELS.get(column, column)}"
    ax.set_title(title)
    ax.set_xlabel(AXIS_LABELS.get(column, column))
    save_plot(fig, f"boxplot_{column}.png", path)


def plot_correlation_heatmap(df: pd.DataFrame, path: str = "outputs/img") -> None:
    """
    Genera el mapa de calor que representa la matriu de correlació de Pearson.

    Args:
        df (pd.DataFrame): Dataset d'anàlisi.
        path (str): Carpeta on exportar la matriu gràfica.

    Returns:
        None
    """
    numeric_df = df.select_dtypes(include=["number"])
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(numeric_df.corr(), annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
    ax.set_title("Mapa de correlacions")
    save_plot(fig, "correlation_heatmap.png", path)


def plot_scatter(df: pd.DataFrame, x_col: str, y_col: str, path: str = "outputs/img") -> None:
    """
    Genera un gràfic de dispersió bivariant per comparar variables.

    Args:
        df (pd.DataFrame): Dataset analític.
        x_col (str): Variable asignada a l'eix de les abscisses.
        y_col (str): Variable asignada a l'eix de les ordenades.
        path (str): Carpeta de sortida del gràfic.

    Returns:
        None
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=df, x=x_col, y=y_col, alpha=0.5, ax=ax)
    ax.set_title("Relació entre audiència i reproduccions (escala logarítmica)")
    ax.set_xlabel(AXIS_LABELS.get(x_col, x_col))
    ax.set_ylabel(AXIS_LABELS.get(y_col, y_col))
    save_plot(fig, f"scatter_{x_col}_vs_{y_col}.png", path)


def plot_genre_popularity(df: pd.DataFrame, path: str = "outputs/img") -> None:
    """
    Dibuixa la ràtio mitjana de popularitat segmentada per gènere musical principal.

    Args:
        df (pd.DataFrame): Dataset analític ampliat.
        path (str): Carpeta on exportar la gràfica.

    Returns:
        None
    """
    genre_cols = ["tag_rock", "tag_pop", "tag_electronic", "tag_hip-hop",  "tag_metal",
        "tag_indie",  "tag_other"]

    popularity_rates = {}

    for col in genre_cols:
        popularity_rates[col] = df[df[col] == 1]["popular"].mean()

    genre_df = pd.DataFrame({"genre": popularity_rates.keys(),
                            "popularity_rate": popularity_rates.values()
                            })

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=genre_df, x="genre", y="popularity_rate", ax=ax)
    ax.set_title("Percentatge d'artistes populars per gènere")
    ax.set_ylabel("Percentatge popularitat")
    ax.set_xlabel("Gènere")
    save_plot(fig, "genre_popularity.png", path)


def plot_genre_comparison(df: pd.DataFrame, path: str = "outputs/img") -> None:
    """
    Compara la distribució de reproduccions logarítmiques entre Rock i Pop amb diagrames de violí.

    Args:
        df (pd.DataFrame): Dataset d'anàlisi.
        path (str): Carpeta final de la imatge.

    Returns:
        None
    """
    rock = df[df['tags'].str.contains('rock', case=False, na=False)].copy()
    rock['genre'] = 'Rock'
    pop = df[df['tags'].str.contains('pop', case=False, na=False)].copy()
    pop['genre'] = 'Pop'

    comparison_df = pd.concat([rock, pop])
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.violinplot(data=comparison_df, x='genre', y='scrobbles_log', ax=ax)
    ax.set_title("Contrast d'engagement entre gèneres Rock i Pop")
    ax.set_xlabel("Gènere")
    ax.set_ylabel(AXIS_LABELS.get("scrobbles_log", "Scrobbles (log)"))
    save_plot(fig, "contrast_rock_vs_pop_violinplot.png", path)


def plot_genre_distributions(df: pd.DataFrame, path: str = "outputs/img") -> None:
    """
    Genera histogrames superposats dels subgrups de Rock i Pop.

    Args:
        df (pd.DataFrame): Dataset d'anàlisi.
        path (str): Carpeta de sortida del fitxer d'imatge.

    Returns:
        None
    """
    rock = df[df['tags'].str.contains('rock', case=False, na=False)]['scrobbles_log']
    pop = df[df['tags'].str.contains('pop', case=False, na=False)]['scrobbles_log']

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(rock, kde=True, label='Rock', alpha=0.5, ax=ax)
    sns.histplot(pop, kde=True, label='Pop', alpha=0.5, ax=ax)
    ax.set_title("Distribucions comparades d'engagement: Rock vs Pop")
    ax.set_xlabel(AXIS_LABELS.get("scrobbles_log", "Scrobbles (log)"))
    ax.set_ylabel("Freqüència")
    ax.legend()
    save_plot(fig, "contrast_rock_vs_pop_distributions.png", path)


def perform_visualization(df: pd.DataFrame) -> None:
    """
    Coordina i genera massivament tots els diagrames definits en el mòdul.

    Args:
        df (pd.DataFrame): Dataset netejat.

    Returns:
        None
    """
    sns.set_palette("muted")

    if df.empty:
        print("Error: No hi ha dades per visualitzar.")
        return

    path = "outputs/img"

    # Distribucions de variables numèriques
    plot_distribution(df, "listeners", path)
    plot_distribution(df, "listeners_log", path)
    plot_distribution(df, "scrobbles", path)
    plot_distribution(df, "scrobbles_log", path)

    # Boxplots per detectar outliers
    plot_boxplot(df, "listeners", path)
    plot_boxplot(df, "scrobbles", path)

    # Correlacions
    plot_correlation_heatmap(df, path)
    plot_scatter(df, "listeners_log", "scrobbles_log", path)

    # Variables categòriques
    plot_categorical_distribution(df, "popular", path)
    plot_genre_popularity(df, path)

    plot_categorical_distribution(df, "popularity_level", path)

    # Gràfics per al contrast d'hipòtesi
    plot_genre_comparison(df, path)
    plot_genre_distributions(df, path)

    print("Visualitzacions generades correctament a la carpeta 'outputs/img/'.")
