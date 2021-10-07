from models import RestaurantResource, Restaurant


def from_restaurant_resource(resource: RestaurantResource, restaurant: Restaurant) -> Restaurant:
    restaurant.name = resource.name
    restaurant.description = resource.description
    return restaurant
