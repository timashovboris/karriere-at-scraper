from matplotlib import pyplot as plt

from karriere_at_scraper.analyser.charts_locales import ChartsLocale


def draw_employment_types_chart(df, locale = "en"):
    locale = ChartsLocale(locale)

    empl_df = df.copy()
    empl_df['Employment type'] = empl_df['Employment type'].str.split(', ')
    empl_df = empl_df.explode('Employment type')

    # Count the occurrences of each unique employment type
    employment_counts = empl_df['Employment type'].value_counts()

    # Plotting the bar chart
    plt.figure(figsize=(8, 6))
    employment_counts.plot(kind='bar')
    plt.title(locale.get("employment_types_title"))
    plt.xlabel('Art der Beschäftigung')
    plt.ylabel(locale.get("employment_types_ylabel"))
    plt.xticks(rotation=30)

    # Calculate the total number of employment types
    total_count = employment_counts.sum()

    # Calculate the percentage for each employment type
    percentages = (employment_counts / total_count) * 100

    # Adding data labels
    for i, (count, percentage) in enumerate(zip(employment_counts, percentages)):
        plt.text(i, count + 0.1, f'{count} ({percentage:.1f}%)', ha='center', va='bottom')

    plt.show()
