import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from karriere_at_scraper.analyser.charts_locales import get_locale

_MIN_SALARY_COL = 'Minimum monthly salary'
_MAX_SALARY_COL = 'Maximum monthly salary'
_AVG_SALARY_COL = 'Average monthly salary'


def _parse_single_salary(salary_str):
    # If salary is unknown
    if pd.isna(salary_str) or salary_str == 'N/A':
        return pd.NA, pd.NA, pd.NA

    # Normalise the string. Turns "1.234,56 €" into "1234.56 €"
    normalized_salary_str = salary_str.replace('.', '').replace(',', '.')

    # Regex to find numbers and units.
    # It looks for one or two floating point numbers and then a unit.
    pattern = re.search(
        r'ab\s*(\d+\.?\d*)\s*€\s*(monatlich|jährlich)|'  # ab X € unit
        r'(\d+\.?\d*)\s*€\s*–\s*(\d+\.?\d*)\s*€\s*(monatlich|jährlich)|'  # X € – Y € unit
        r'(\d+\.?\d*)\s*€\s*(monatlich|jährlich)',  # X € unit
        normalized_salary_str
    )

    # If no pattern matched
    if not pattern:
        return pd.NA, pd.NA, pd.NA

    min_salary = pd.NA
    max_salary = pd.NA
    average_salary = pd.NA
    unit = None

    # Determine which group matched and extract values and unit
    if pattern.group(1) is not None:  # "ab X € unit" pattern
        min_salary = float(pattern.group(1))
        unit = pattern.group(2)
        max_salary = pd.NA  # Max is unknown because "ab" technically means "starting from"
        average_salary = min_salary
    elif pattern.group(3) is not None:  # "X € – Y € unit" pattern
        min_salary = float(pattern.group(3))
        max_salary = float(pattern.group(4))
        unit = pattern.group(5)
        average_salary = (min_salary + max_salary) / 2
    elif pattern.group(6) is not None:  # "X € unit" pattern, if ever encountered
        min_salary = float(pattern.group(6))
        max_salary = min_salary
        average_salary = min_salary
        unit = pattern.group(7)

    # Convert yearly salaries to monthly
    if unit == 'jährlich':
        if pd.notna(min_salary):
            min_salary /= 12
        if pd.notna(max_salary):
            max_salary /= 12
        if pd.notna(average_salary):  # Make sure average is also converted
            average_salary /= 12

    return min_salary, max_salary, average_salary


# Add minimum and maximum monthly salaries to dataframe
def process_salaries(df):
    df[[_MIN_SALARY_COL, _MAX_SALARY_COL, _AVG_SALARY_COL]] = df['Salary'].apply(
        lambda x: pd.Series(_parse_single_salary(x)))


def draw_salaries_chart(df, locale = "en"):
    salaries = df[_AVG_SALARY_COL].dropna().tolist()

    q25 = np.percentile(salaries, 25)
    q75 = np.percentile(salaries, 75)

    # Calculate the Interquartile Range (IQR)
    iqr = q75 - q25

    # Define the outlier fences
    # A common rule of thumb is 1.5 * IQR
    lower_bound = q25 - 1.5 * iqr
    upper_bound = q75 + 1.5 * iqr

    salaries = [salary for salary in salaries if lower_bound <= salary <= upper_bound]

    mean_salary = np.mean(salaries)
    median_salary = np.median(salaries)

    # Define bins
    bins = np.histogram_bin_edges(salaries, bins='fd')

    # Create histogram
    plt.figure(figsize=(13, 5))
    ax = sns.histplot(salaries, bins=bins, kde=True)

    # Get bin counts and normalize to percentages
    counts, _ = np.histogram(salaries, bins=bins)
    total = len(salaries)
    percentages = (counts / total) * 100

    # Add percentage labels on each bin
    for rect, percentage in zip(ax.patches, percentages):
        height = rect.get_height()
    ax.text(rect.get_x() + rect.get_width() / 2, height + 1, f'{percentage:.1f}%',
            ha='center', fontsize=10, color='black')

    label_texts = get_locale(locale)

    # Add mean and median lines
    plt.axvline(mean_salary, color='red', linestyle='dashed', linewidth=2, label=f'{label_texts.get("avg")}: {mean_salary:,.0f} €')
    plt.axvline(median_salary, color='green', linestyle='dashed', linewidth=2, label=f'{label_texts.get("med")}: {median_salary:,.0f} €')
    plt.axvline(q25, linewidth=1, label=f'{label_texts.get("q25")}: {q25:,.0f} €')
    plt.axvline(q75, linewidth=1, label=f'{label_texts.get("q75")}: {q75:,.0f} €')

    # Format x-axis labels with bin ranges
    bin_labels = [f"{int(bins[i])} € - {int(bins[i + 1])} €" for i in range(len(bins) - 1)]
    plt.xticks((bins[:-1] + bins[1:]) / 2, bin_labels, rotation=60)

    # Labels and title
    plt.xlabel(label_texts.get("salaries_xlabel"))
    plt.ylabel(label_texts.get("salaries_ylabel"))
    plt.title(label_texts.get("salaries_title"))

    # Show legend
    plt.legend()
    plt.show()
