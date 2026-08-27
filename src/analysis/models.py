# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=too-many-locals
"""
Mòdul de modelització de dades.

Entrena i avalua models supervisats (Random Forest) i algorismes de
clustering no supervisats (K-Means).
"""

from typing import Tuple, List, Dict, Any
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.metrics import (
    silhouette_score,
    silhouette_samples,
    accuracy_score,
    classification_report,
    confusion_matrix
)
from sklearn.preprocessing import StandardScaler
from src.analysis.visualization import save_plot, AXIS_LABELS


def prepare_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, List[str]]:
    """
    Separa les variables predictives de la variable objectiu del model supervisat.

    Args:
        df (pd.DataFrame): Dataset complet amb les característiques creades.

    Returns:
        Tuple[pd.DataFrame, pd.Series, List[str]]: Matriu de característiques X,
            vector target y, i llista de noms de les variables seleccionades.
    """
    features: List[str] = [
        "scrobbles_log",
        "age",
        "tag_rock",
        "tag_pop",
        "tag_electronic",
        "tag_hip-hop",
        "tag_metal",
        "tag_indie",
        "tag_other"
    ]

    X: pd.DataFrame = df[features]
    y: pd.Series = df["popular"]

    return X, y, features


def split_data(
        X: pd.DataFrame,
        y: pd.Series,
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Divideix els vectors de dades en conjunts d'entrenament i de test.

    Args:
        X (pd.DataFrame): Matriu de característiques.
        y (pd.Series): Variable objectiu.
        test_size (float): Proporció de dades assignades al test (per defecte 0.2).
        random_state (int): Llavor de replicabilitat (per defecte 42).

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
            Conjunts X_train, X_test, y_train, y_test.
    """
    return train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=y)


def scale_features(
        X_train: pd.DataFrame,
        X_test: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray, StandardScaler]:
    """
    Standarditza les característiques aplicant una transformació de puntuació Z.

    Args:
        X_train (pd.DataFrame): Característiques d'entrenament.
        X_test (pd.DataFrame): Característiques de test.

    Returns:
        Tuple[np.ndarray, np.ndarray, StandardScaler]:
            Matrius transformades de train i test, i l'objecte scaler ajustat.
    """
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    return X_train_scaled, X_test_scaled, scaler


def train_random_forest(
        X_train: np.ndarray,
        y_train: pd.Series,
        random_state: int = 42
    ) -> RandomForestClassifier:
    """
    Entrena un model de classificació Random Forest optimitzat.

    Args:
        X_train (np.ndarray): Característiques d'entrenament escalades.
        y_train (pd.Series): Variable objectiu d'entrenament.
        random_state (int): Llavor de replicabilitat.

    Returns:
        RandomForestClassifier: Model de Random Forest entrenat.
    """
    model = RandomForestClassifier(n_estimators=100,
                                   random_state=random_state,
                                   class_weight="balanced"
                                   )

    model.fit(X_train, y_train)

    return model


def evaluate_model(
        model: RandomForestClassifier,
        X_test: np.ndarray,
        y_test: pd.Series
    ) -> Tuple[Dict[str, Any], np.ndarray]:
    """
    Calcula les mètriques d'avaluació i les prediccions del model supervisat.

    Args:
        model (RandomForestClassifier): Model entrenat.
        X_test (np.ndarray): Característiques de validació escalades.
        y_test (pd.Series): Valors reals de validació.

    Returns:
        Tuple[Dict[str, Any], np.ndarray]:
            Diccionari amb precisió, informe i matriu de confusió, i vector de prediccions.
    """
    y_pred = model.predict(X_test)
    results = {
        "accuracy": accuracy_score(y_test, y_pred),
        "classification_report": classification_report(y_test, y_pred),
        "confusion_matrix": confusion_matrix(y_test, y_pred)
    }

    return results, y_pred


def get_feature_importance(
        model: RandomForestClassifier,
        feature_names: List[str]
    ) -> pd.DataFrame:
    """
    Extreu i ordena la importància de les variables basada en el model entrenat.

    Args:
        model (RandomForestClassifier): Model de Random Forest.
        feature_names (List[str]): Noms de les variables utilitzades.

    Returns:
        pd.DataFrame: Taula ordenada amb la importància relativa de cada variable.
    """
    importance_df = pd.DataFrame({
                                "feature": feature_names,
                                "importance": model.feature_importances_
                                })

    return importance_df.sort_values(by="importance", ascending=False)


def plot_confusion_matrix(matrix: np.ndarray, path: str = "outputs/img") -> None:
    """
    Genera i desa el mapa de calor representatiu de la matriu de confusió.

    Args:
        matrix (np.ndarray): Matriu numèrica de confusió.
        path (str): Ruta on es vol desar la imatge generada.

    Returns:
        None
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(matrix, annot=True, fmt="d", cmap="Blues",  ax=ax)
    ax.set_title("Matriu de confusió")
    ax.set_xlabel("Predicció")
    ax.set_ylabel("Valor real")
    save_plot(fig, "confusion_matrix.png", path)


def plot_feature_importance(importance_df: pd.DataFrame, path: str = "outputs/img") -> None:
    """
    Dibuixa i exporta el gràfic de barres d'importància de característiques.

    Args:
        importance_df (pd.DataFrame): DataFrame ordenat amb les importàncies.
        path (str): Ruta on desar el gràfic.

    Returns:
        None
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=importance_df, x="importance", y="feature", ax=ax)
    ax.set_title("Importància de les variables")
    ax.set_xlabel("Importància")
    ax.set_ylabel("Variable")
    save_plot(fig, "feature_importance.png", path)


def random_forest_pipeline(
        df: pd.DataFrame,
        path: str = "outputs/img"
    ) -> Tuple[RandomForestClassifier, Dict[str, Any], pd.DataFrame]:
    """
    Executa de forma integral el pipeline del model supervisat.

    Args:
        df (pd.DataFrame): Dataset netejat.
        path (str): Carpeta on exportar les gràfiques resultants.

    Returns:
        Tuple[RandomForestClassifier, Dict[str, Any], pd.DataFrame]:
            Model entrenat, diccionari de mètriques i dades d'importància.
    """
    X, y, features = prepare_features(df)
    X_train, X_test, y_train, y_test = split_data(X, y)
    X_train_scaled, X_test_scaled, _ = scale_features(X_train, X_test)
    model = train_random_forest(X_train_scaled, y_train)
    results, _ = evaluate_model(model, X_test_scaled, y_test)
    importance_df = get_feature_importance(model, features)

    plot_confusion_matrix(results["confusion_matrix"], path)
    plot_feature_importance(importance_df, path)

    return model, results, importance_df


def run_clustering_model(
        df: pd.DataFrame,
        n_clusters: int = 3
    ) -> Tuple[pd.DataFrame, float]:
    """
    Executa l'algorisme K-Means per agrupar els artistes segons mètriques de reproducció.

    Args:
        df (pd.DataFrame): Dataset netejat d'anàlisi.
        n_clusters (int): Nombre de clústers a generar (per defecte 3).

    Returns:
        Tuple[pd.DataFrame, float]:
            Dataset original amb la columna 'cluster' assignada i la puntuació de Silhouette.
    """
    df = df.copy()
    # Seleccionem dades numèriques per al clustering
    data_to_cluster = df[['listeners', 'scrobbles']]

    # Normalització (recomanada per a K-Means)
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data_to_cluster)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df['cluster'] = kmeans.fit_predict(data_scaled)

    # Avaluació: Silhouette Score (com de ben separats estan els grups)
    sil_score = silhouette_score(data_scaled, df['cluster'])
    print(f"Silhouette Score per {n_clusters} clústers: {round(sil_score, 4)}")

    return df, round(sil_score, 4)


def plot_clusters(df: pd.DataFrame, path: str = "outputs/img") -> None:
    """
    Genera un gràfic de dispersió bivariant pintat segons els clústers de K-Means.

    Args:
        df (pd.DataFrame): Dataset que inclou les etiquetes del clúster.
        path (str): Directori on exportar la imatge.

    Returns:
        None
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    sns.scatterplot(data=df, x='listeners', y='scrobbles',
                    hue='cluster', palette='viridis', alpha=0.5, ax=ax)

    ax.set_title("Clústers d'artistes (K-Means)")
    ax.set_xlabel(AXIS_LABELS.get("listeners", "Listeners"))
    ax.set_ylabel(AXIS_LABELS.get("scrobbles", "Scrobbles"))
    save_plot(fig, "clusters_kmeans.png", path)


def plot_silhouette(df: pd.DataFrame, path: str = "outputs/img") -> None:
    """
    Dibuixa el diagrama de Silhouette per avaluar visualment la cohesió dels grups.

    Args:
        df (pd.DataFrame): Dataset clasteritzat.
        path (str): Carpeta de destinació del gràfic.

    Returns:
        None
    """
    data = df[['listeners', 'scrobbles']]
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data)

    sample_silhouette_values = silhouette_samples(data_scaled, df['cluster'])
    fig, ax = plt.subplots(figsize=(10, 6))
    y_lower = 10

    colors = plt.colormaps['viridis'](np.linspace(0, 1, df['cluster'].nunique()))

    for i in range(df['cluster'].nunique()):
        cluster_values = sample_silhouette_values[df['cluster'] == i]
        cluster_values.sort()

        y_upper = y_lower + len(cluster_values)
        ax.fill_betweenx(np.arange(y_lower, y_upper), 0, cluster_values,
                         alpha=0.7, color=colors[i])
        ax.text(-0.05, y_lower + 0.5 * len(cluster_values), str(i))
        y_lower = y_upper + 10

    sil_avg = sample_silhouette_values.mean()
    ax.axvline(x=sil_avg, color="red", linestyle="--", label=f"Mitjana: {sil_avg:.4f}")
    ax.set_title("Anàlisi de Silhouette per clúster")
    ax.set_xlabel("Coeficient de Silhouette")
    ax.set_ylabel("Clúster")
    ax.legend()
    save_plot(fig, "silhouette_analysis.png", path)


def perform_modeling(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Coordina de manera centralitzada la creació, validació i exportació dels models.

    Args:
        df (pd.DataFrame): Dataset completament netejat.

    Returns:
        Dict[str, Any]: Diccionari amb un resum de les mètriques dels dos tipus de models.
    """
    sns.set_palette("muted")
    print("\n--- Executant Models de Machine Learning ---")

    # Model Supervisat: Random Forest
    _, results_rf, importance_df = random_forest_pipeline(df)
    print(f"Random Forest Accuracy: {results_rf['accuracy']:.4f}")
    print(f"\nClassification Report:\n{results_rf['classification_report']}")

    # Model No Supervisat: K-Means
    df_clustered, sil_score = run_clustering_model(df)
    plot_clusters(df_clustered)
    plot_silhouette(df_clustered)
    print(df_clustered.groupby('cluster')[['listeners', 'scrobbles']].mean())

    # Combinem resultats per al report
    all_results = {
        "supervisat": {
            "model": "Random Forest",
            "accuracy": round(results_rf['accuracy'], 4),
            "feature_importance": importance_df.to_dict('records')
        },
        "no_supervisat": {
            "model": "K-Means (k=3)",
            "silhouette_score": sil_score
        }
    }

    return all_results
