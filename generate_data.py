import pandas as pd
import numpy as np

np.random.seed(42)
num_samples = 500

days = np.random.randint(2, 15, size=num_samples)   
people = np.random.randint(1, 6, size=num_samples)     
style_numeric = np.random.randint(0, 3, size=num_samples) 

style_cost_multiplier = np.choose(style_numeric, [40.0, 120.0, 350.0])


flight_cost_per_person = np.random.normal(500.0, 150.0, size=num_samples)


predicted_true_cost = (days * people * style_cost_multiplier) + (people * flight_cost_per_person)

predicted_true_cost *= np.random.uniform(0.85, 1.15, size=num_samples)

budget = predicted_true_cost * np.random.uniform(0.60, 1.40, size=num_samples)
budget = np.round(budget / 10) * 10 # Round cleanly to the nearest $10 bill

stayed_under_budget = (budget >= predicted_true_cost).astype(int)

dataset = pd.DataFrame({
    'budget': budget.astype(int),
    'days': days,
    'people': people,
    'style_numeric': style_numeric,
    'stayed_under_budget': stayed_under_budget
})

dataset.to_csv("historical_trips.csv", index=False)
print("📊 Generated 'historical_trips.csv' successfully with 500 trip patterns!")
