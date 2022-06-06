## Daily Exercise

Similar to today's lesson on build in a full CRUD API, develop an API to store your favorite Harry Potter characters:

- Use a DataFrame (or dict) to store the characters in your flask app
- Implement two methods to query characters (_GET_) and another to create new characters (_POST_)
- Each character should have at least two fields: _name_ and _house_
- Your _GET_ method should be able to query characters by either their _name_ or _house_
- Your _POST_ method should accept JSON requests to add new characters. You can simplify this method by allowing to add only a single character per request. The JSON body includes the fields for a new character to add. Check to ensure that you are provided with _name_ and _house_ fields.
- Both methods should respond back with a JSON body.

**Bonus**:
- If time allows, add two other methods to _PATCH_ and _DELETE_.
  