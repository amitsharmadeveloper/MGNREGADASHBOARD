import os
import pandas as pd
from django.conf import settings
from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def district_dashboard(request, state, district, year, month=None):
    """
    Loads MGNREGA district data (year-wise or month-wise) from local CSV files.
    """

    filename = f"mgnrega_{year.replace('-', '_')}.csv"
    csv_path = os.path.join(settings.BASE_DIR, "dashboard", "data", filename)

    if not os.path.exists(csv_path):
        return render(request, "dashboard.html", {
            "district_name": district,
            "year": year,
            "month": month,
            "error": f"Data file for {year} not found.",
        })

    try:
        df = pd.read_csv(csv_path)
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

        required_cols = ['state_name', 'district_name']
        for col in required_cols:
            if col not in df.columns:
                raise KeyError(f"Missing column '{col}' in CSV file")

        filtered_data = df[
            (df['state_name'].str.lower().str.strip() == state.lower().strip()) &
            (df['district_name'].str.lower().str.strip() == district.lower().strip())
        ]

        if month:
            month = month.strip().lower()
            if 'month' in df.columns:
                filtered_data = filtered_data[filtered_data['month'].str.lower().str.strip() == month]

        if filtered_data.empty:
            msg = f"No records found for {district}, {state} ({year})"
            if month:
                msg += f" - {month.capitalize()}"
            return render(request, "dashboard.html", {
                "district_name": district,
                "state_name": state,
                "year": year,
                "month": month,
                "error": msg,
            })

        records = filtered_data.to_dict(orient='records')

        total_budget = filtered_data['approved_labour_budget'].sum() if 'approved_labour_budget' in filtered_data.columns else 0
        avg_wage = filtered_data['average_wage_rate_per_day_per_person'].mean() if 'average_wage_rate_per_day_per_person' in filtered_data.columns else 0
        avg_employment_days = filtered_data['average_days_of_employment_provided_per_household'].mean() if 'average_days_of_employment_provided_per_household' in filtered_data.columns else 0

        months, wage_trend, employment_trend = [], [], []
        if 'month' in filtered_data.columns:
            filtered_data['month'] = (
                filtered_data['month']
                .str.strip()
                .str.capitalize()
                .replace({
                    'Apr': 'April', 'Jun': 'June', 'Jul': 'July', 'Aug': 'August',
                    'Sep': 'September', 'Oct': 'October', 'Nov': 'November', 'Dec': 'December',
                    'Jan': 'January', 'Feb': 'February', 'Mar': 'March'
                })
            )

            month_order = ["April", "May", "June", "July", "August", "September",
                           "October", "November", "December", "January", "February", "March"]

            trend_df = filtered_data.groupby('month', as_index=False).agg({
                'average_wage_rate_per_day_per_person': 'mean',
                'average_days_of_employment_provided_per_household': 'mean'
            })

            trend_df['month'] = pd.Categorical(trend_df['month'], categories=month_order, ordered=True)
            trend_df = trend_df.sort_values('month').dropna(subset=['month'])

            months = trend_df['month'].tolist()
            wage_trend = trend_df['average_wage_rate_per_day_per_person'].round(2).tolist()
            employment_trend = trend_df['average_days_of_employment_provided_per_household'].round(2).tolist()

        context = {
            "district_name": district,
            "state_name": state,
            "year": year,
            "records": records,
            "total_records": len(records),
            "total_budget": round(total_budget, 2),
            "avg_wage": round(avg_wage, 2),
            "avg_employment_days": round(avg_employment_days, 2),
            "months": months,
            "wage_trend": wage_trend,
            "employment_trend": employment_trend,
        }

        if month:
            context["month"] = month.capitalize()

        return render(request, "dashboard.html", context)

    except Exception as e:
        return render(request, "dashboard.html", {
            "district_name": district,
            "state_name": state,
            "year": year,
            "month": month,
            "error": f"Error reading CSV: {str(e)}",
        })
