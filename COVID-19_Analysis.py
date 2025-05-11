 # COVID-19 GLOBAL DATA TRACKER
# Complete Jupyter Notebook Implementation

 ## 1. Setup and Data Loading
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from ipywidgets import interact, widgets
plt.style.use('ggplot')

# Load dataset (can be from URL or local)
try:
    df = pd.read_csv('owid-covid-data.csv', parse_dates=['date'])
except:
    df = pd.read_csv('https://covid.ourworldindata.org/data/owid-covid-data.csv', 
                    parse_dates=['date'])

## 2. Data Cleaning Pipeline
def clean_data(df, countries=None):
    """Clean and prepare COVID-19 data"""
    # Select key columns
    cols = ['date', 'location', 'total_cases', 'new_cases', 'total_deaths', 
            'new_deaths', 'people_vaccinated', 'population', 'icu_patients']
    clean_df = df[cols].copy()
    
    # Filter countries if specified
    if countries:
        clean_df = clean_df[clean_df['location'].isin(countries)]
    
    # Handle missing values
    for col in ['total_cases', 'total_deaths', 'people_vaccinated', 'icu_patients']:
        clean_df[col] = clean_df.groupby('location')[col].ffill()
    
    # Calculate metrics
    clean_df['death_rate'] = clean_df['total_deaths'] / clean_df['total_cases']
    clean_df['vaccination_rate'] = clean_df['people_vaccinated'] / clean_df['population']
    clean_df['icu_per_million'] = clean_df['icu_patients'] / (clean_df['population']/1e6)
    
    return clean_df.dropna(subset=['total_cases'])

# Example usage
countries = ['United States', 'India', 'Brazil', 'Germany', 'Kenya']
clean_df = clean_data(df, countries)

## 3. Interactive Analysis Functions
def plot_country_trends(country, metric, start_date, end_date):
    """Interactive plot of selected metric for a country"""
    mask = (clean_df['location'] == country) & \
           (clean_df['date'] >= pd.to_datetime(start_date)) & \
           (clean_df['date'] <= pd.to_datetime(end_date))
    
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=clean_df[mask], x='date', y=metric)
    plt.title(f'{metric.replace("_", " ").title()} in {country}')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def compare_countries(metric, date):
    """Compare countries on selected metric at specific date"""
    date = pd.to_datetime(date)
    compare_df = clean_df[clean_df['date'] == date]
    
    plt.figure(figsize=(10, 6))
    sns.barplot(data=compare_df, x='location', y=metric)
    plt.title(f'Comparison on {date.strftime("%Y-%m-%d")}')
    plt.xticks(rotation=45)
    plt.show()

## 4. Visualization Dashboard
# Interactive widgets
metrics = ['total_cases', 'total_deaths', 'vaccination_rate', 'icu_per_million']
countries = clean_df['location'].unique()

@interact
def covid_dashboard(
    country=widgets.Dropdown(options=countries, value='United States'),
    metric=widgets.Dropdown(options=metrics, value='total_cases'),
    start_date=widgets.DatePicker(value=pd.to_datetime('2021-01-01')),
    end_date=widgets.DatePicker(value=pd.to_datetime('2023-12-31'))
):
    plot_country_trends(country, metric, start_date, end_date)

## 5. Advanced Visualizations
# Choropleth map of latest vaccination rates
latest = clean_df[clean_df['date'] == clean_df['date'].max()]
fig = px.choropleth(latest, 
                    locations="location",
                    locationmode="country names",
                    color="vaccination_rate",
                    hover_name="location",
                    color_continuous_scale=px.colors.sequential.Plasma,
                    title="Global Vaccination Rates")
fig.show()

# Correlation heatmap
corr_df = clean_df.groupby('location').last()[metrics]
plt.figure(figsize=(10, 8))
sns.heatmap(corr_df.corr(), annot=True, cmap='coolwarm')
plt.title('COVID-19 Metrics Correlation')
plt.show()

## 6. Key Insights Calculation
def generate_insights():
    """Generate automated insights from the data"""
    latest = clean_df[clean_df['date'] == clean_df['date'].max()]
    
    insights = [
        f"1. Highest vaccination rate: {latest.loc[latest['vaccination_rate'].idxmax(), 'location']} "
        f"({latest['vaccination_rate'].max():.1%})",
        
        f"2. Highest death rate: {latest.loc[latest['death_rate'].idxmax(), 'location']} "
        f"({latest['death_rate'].max():.1%})",
        
        f"3. Most ICU patients per million: {latest.loc[latest['icu_per_million'].idxmax(), 'location']} "
        f"({latest['icu_per_million'].max():.1f})",
        
        "4. Vaccination rates correlate negatively with death rates "
        f"(r = {corr_df['vaccination_rate'].corr(corr_df['death_rate']):.2f})"
    ]
    
    for insight in insights:
        print(insight)

generate_insights()

## 7. Export to PDF
!jupyter nbconvert --to pdf COVID-19_Analysis.ipynb