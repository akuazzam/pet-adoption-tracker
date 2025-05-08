from function_.business_functions import (
    get_top_recommended_pets_for_user,
    get_most_adoptable_pet_profiles,
    get_top_crossdb_user_connections,
    get_low_engagement_pets_report,
    get_user_engagement_report,
    forecast_pet_demand_by_breed_or_tag
)


def run_example_calls():
    # Example parameters
    user_id = 1
    top_n = 5

    # 1) Top recommended pets for a user
    recommendations = get_top_recommended_pets_for_user(user_id, top_n)
    print("Top Recommended Pets for user {}: {}".format(user_id, recommendations))

    # 2) Most adoptable pet profiles
    adoptable = get_most_adoptable_pet_profiles(top_n)
    print(f"Most Adoptable Pets (top {top_n}): {adoptable}")

    # 3) Top cross-db user connections
    connections = get_top_crossdb_user_connections(user_id, top_n)
    print(f"Top {top_n} Cross-DB Connections for user {user_id}: {connections}")

    # 4) Low engagement pets report
    low_engagement = get_low_engagement_pets_report()
    print(f"Low Engagement Pets: {low_engagement}")

    # 5) User engagement report
    engagement_report = get_user_engagement_report(user_id)
    print(f"Engagement Report for user {user_id}: {engagement_report}")

    # 6) Forecast pet demand by breed or tag
    forecast = forecast_pet_demand_by_breed_or_tag()
    print(f"Forecast Pet Demand by Breed and Tag: {forecast}")


if __name__ == '__main__':
    run_example_calls()
