# -*- coding: utf-8 -*-
"""
Mòdul principal i arrel del programa.

Coordina de manera seqüencial l'execució completa de totes les etapes del
pipeline (Càrrega, Neteja, Visualització, Estadística i Modelització).
"""

import matplotlib.pyplot as plt
import seaborn as sns
from src.processing import loading
from src.processing import cleaning
from src.analysis import visualization
from src.analysis import statistics
from src.analysis import models
from src.analysis.visualization import save_plot
from src import utils



def main() -> None:
    """
    Orquestra el flux d'execució complet del cicle de vida de les dades.

    Returns:
        None
    """
    # Configurem de l'analitzador d'arguments.
    # Preparació de l'entorn (Assegurem que existeixin les carpetes de sortida)
    utils.ensure_directories(['outputs/img', 'outputs/reports', 'outputs/data'])

    # ---------------------------------------------------------
    # ETAPA 1: Càrrega i Exploració
    # ---------------------------------------------------------
    df_bs4 = loading.load_dataset("data/artists_bs4.csv")
    df_crawl = loading.load_dataset("data/dataset_crawler.csv")

    utils.format_console_header("EDA: Dades BeautifulSoup")
    utils.generate_eda_log(df_bs4, "artists_bs4.csv (original)",
                       loading.perform_eda,
                       filename="eda_pre_cleaning.txt")

    # Boxplots pre-neteja
    for col in ["listeners", "scrobbles"]:
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.boxplot(data=df_bs4, x=col, ax=ax)
        ax.set_title(f"Boxplot de {col} (pre-neteja)")
        save_plot(fig, f"boxplot_{col}_pre_cleaning.png", "outputs/img")

    utils.format_console_header("EDA: Dades Crawler")
    loading.perform_eda(df_crawl)

    # ---------------------------------------------------------
    # ETAPA 2: Integració i Neteja
    # ---------------------------------------------------------
    utils.format_console_header("Etapa 2: Integració i Neteja")
    df_clean = cleaning.perform_cleaning(df_bs4)

    # EDA post-neteja per comparar l'abans i el després
    utils.format_console_header("EDA post-neteja")
    utils.generate_eda_log(df_clean, "lastfm_clean.csv (net)",
                       loading.perform_eda,
                       filename="eda_post_cleaning.txt")

    # Desem el dataset net
    df_clean.to_csv("outputs/data/lastfm_clean.csv", index=False)
    print("Dataset net desat a: outputs/data/lastfm_clean.csv")

    # ---------------------------------------------------------
    # ETAPA 3: Visualització
    # ---------------------------------------------------------
    utils.format_console_header("Etapa 3: Visualitzacions")
    visualization.perform_visualization(df_clean)

    # ---------------------------------------------------------
    # ETAPA 4: Estadística i Contrastos
    # ---------------------------------------------------------
    utils.format_console_header("Etapa 4: Anàlisi estadística")
    stats_results = statistics.perform_statistical_analysis(df_clean)
    utils.save_report(stats_results, filename="stats_report.json")

    # ---------------------------------------------------------
    # ETAPA 5: Models
    # ---------------------------------------------------------
    utils.format_console_header("Etapa 5: Models Supervisats i No Supervisats")
    model_metrics = models.perform_modeling(df_clean)
    utils.save_report(model_metrics, filename="models_report.json")

if __name__ == "__main__":
    main()
