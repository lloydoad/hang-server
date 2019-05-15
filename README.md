# HANG SERVER
A control center, database manager, and API manager for hang react app. [Control Center](https://hang-server.herokuapp.com/)

### Available Routes
#### Base URL
```https://hang-server.herokuapp.com```

#### Fetch Available Events
**Note**: Pagination not currently enabled. Date fetch request data can be potentially large.

| Result                                                | Route               | Format                                   |
| -------------                                         |:-------------       | :-------------                           |
| Specific event by id                                  | ```/events/id```    |```/<string:eventid>```                   |
| Events for specific day                               | ```/events/dayof``` |```/<int:year>/<int:month>/<int:day>```   |
| Events for specific week (starts at given day)        | ```/events/weekof```|```/<int:year>/<int:month>/<int:day>```   |
| Events within geographic radius                       | ```/events/range``` |```/<double:latitude>,<double:longitude>,<double:radius>```    |

#### Manage Database
