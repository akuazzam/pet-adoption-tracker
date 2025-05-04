from function_.business_functions import forecast_pet_demand_by_breed_or_tag

forecast = forecast_pet_demand_by_breed_or_tag()
print("📈 Demand vs Supply by Breed:")
for breed, stats in forecast["by_breed"].items():
    print(f" • {breed}: demand={stats['demand']}, supply={stats['supply']}, ratio={stats['ratio']}")
print("\n📈 Demand vs Supply by Tag:")
for tag, stats in forecast["by_tag"].items():
    print(f" • {tag}: demand={stats['demand']}, supply={stats['supply']}, ratio={stats['ratio']}")
