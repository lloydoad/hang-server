# HANG SERVER
A control center, database manager, and API manager for hang react app. [Control Center](https://hang-server.herokuapp.com/)

## Available Routes
### Base URL
```https://hang-server.herokuapp.com```

### Fetch Events
**Note**: *Pagination not currently enabled. Date fetch request data can be potentially large.*

| Result                                                | Route               | Format                                   |
| -------------                                         |:-------------       | :-------------                           |
| Specific event by id                                  | ```/events/id```    |```/<string:eventid>```                   |
| Events for specific day                               | ```/events/dayof``` |```/<int:year>/<int:month>/<int:day>```   |
| Events for specific week (starts at given day)        | ```/events/weekof```|```/<int:year>/<int:month>/<int:day>```   |
| Events within geographic radius                       | ```/events/range``` |```/<double:latitude>,<double:longitude>,<double:radius>```    |

### Manage Database
**Note**: *Requests without valid ClientIDs will be rejected. ClientIDs can be generated from control center*

**Example**: `https://hang-server.herokuapp.com/toggleDatabase?clientid=<CLIENTID>&switch=seatGeekData`

| Action                          | Route                  | Required Query Data                            |
| -------------                   |:-------------          | :-------------                                 |
| Toggle a database source        | ```/toggleDatabase?``` |```clientid:<String>, switch:<String>```        |
| Update events for specific city | ```/update?```         |```clientid:<String>, city:<String>```          |
| Delete specific event           | ```/delete?```         |```clientid:<String>, eventid:<String>```       |
| Remove past events              | ```/clean?```          |```clientid:<String>```                          |
| Add attendant and tag list      | ```/addAttendant?```   |```clientid:<String>, eventid:<String>, uuid:<String>, tags:<String List>```   |
| Remove attendant and tag list   | ```/removeAttendant?```|```clientid:<String>, eventid:<String>, uuid:<String>, tags:<String List>```   |
