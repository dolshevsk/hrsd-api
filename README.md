# hrsd-api
It’s a restaurant API where you can create, update and delete a restaurant (identified by its name), and also list restaurants, get a restaurant by name and get a random restaurant.

## 👨‍💻 to launch a project
1. create .env according to .env.example file (default POSTGRES_HOST=postgres)
2. `docker-compose up`

## 📝 API
* welcome page `GET /`
* list restaurants `GET /restaurants`
* create restaurant `POST /restaurants`
* retrieve restaurant `GET /restaurants/{name}`
* random restaurant `GET /random-restaurant`
* update restaurant `PUT /restaurants/{name}`
* remove restaurant `DELETE /restaurants/{name}`