from app.services.finance import annual_series,growth_rates
def test_growth():
    x=[{"form":"10-K","concept":"Revenue","end":"2024-01-01","value":100},
       {"form":"10-K","concept":"Revenue","end":"2025-01-01","value":120}]
    assert growth_rates(annual_series(x))[0]["growth_pct"]==20.0
