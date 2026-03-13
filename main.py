import random
from fastapi import FastAPI, Query , Body , Cookie , Header , status ,  Form, File
from enum import Enum
from pydantic import BaseModel, AfterValidator , Field , HttpUrl
from typing import Annotated


app = FastAPI()


@app.get("/")
def root():
    """
    Root endpoint that returns a welcome message.

    This is the main entry point of the API, providing a simple greeting
    to confirm the API is running.
    """
    return {"message": "Hello World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    """
    Retrieve an item by its ID.

    This endpoint demonstrates path parameters by accepting an integer item_id
    and returning it in the response.
    """
    return {"item_id": item_id}


@app.get("/users")
async def read_users():
    """
    Get a list of users.

    Returns a simple list of user names for demonstration purposes.
    """
    return ["Rick", "Morty"]


@app.get("/users2")
async def read_users2():
    """
    Get an alternative list of users.

    Returns a different set of user names to demonstrate multiple endpoints
    serving similar data.
    """
    return ["Bean", "Elfo"]


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    """
    Get information about a machine learning model.

    This endpoint demonstrates the use of Enum path parameters. It accepts
    one of the predefined model names (alexnet, resnet, lenet) and returns
    model-specific information.
    """
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    """
    Get information about a file path.

    This endpoint demonstrates path parameters that can contain slashes
    by using the :path converter. It accepts any file path and returns it.
    """
    return {"file_path": file_path}


fake_items_db = [
    {"item_name": "Foo"},
    {"item_name": "Bar"},
    {"item_name": "Baz"},
]


@app.get("/pageitems/")
async def read_item(skip: int = 0, limit: int = 10):
    """
    Get paginated items from the database.

    This endpoint demonstrates query parameters for pagination. It accepts
    'skip' (offset) and 'limit' (maximum number of items) parameters to
    implement basic pagination.
    """
    return fake_items_db[skip: skip + limit]


@app.get("/querydemo/{item_id}")
async def read_query_item(item_id: int, q: str | None = None, short: bool = False):
    """
    Get an item with optional query parameters.

    This endpoint demonstrates optional query parameters. It accepts an item_id
    as a path parameter and optional 'q' (query string) and 'short' (boolean)
    query parameters that modify the response.
    """
    item = {"item_id": item_id, "short": short, "q": q}

    if q:
        item.update({"q": q})

    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )

    return item


@app.get("/needyitems/{item_id}")
async def read_user_item(item_id: str, needy: str):
    """
    Get a user item with a required needy parameter.

    This endpoint demonstrates required query parameters. Both the item_id
    (path parameter) and 'needy' (query parameter) are required for this request.
    """
    item = {"item_id": item_id, "needy": needy}
    return item


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


@app.post("/postitems/")
async def create_item(item: Item):
    """
    Create a new item.

    This endpoint demonstrates POST requests with Pydantic models as request bodies.
    It accepts an Item object and optionally calculates the price with tax if provided.
    """
    item_dict = item.model_dump()

    if item.tax is not None:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})

    return item_dict


@app.put("/postitems/{item_id}")
async def update_item(item_id: int, item: Item):
    """
    Update an existing item.

    This endpoint demonstrates PUT requests for updating resources. It combines
    path parameters (item_id) with request body data (Item model) to update an item.
    """
    return {"item_id": item_id, **item.model_dump()}


@app.get("/searchitems/")
async def read_search_items(
    q: Annotated[
        str,
        Query(
            alias="mobile",
            title="Query string",
            description="Query string for searching items",
            min_length=3,
            max_length=50,
            pattern="^\d{10}$",
            deprecated=True,
        ),
    ]
):
    """
    Search for items using a mobile number query.

    This endpoint demonstrates advanced query parameter validation using Annotated
    types with Query constraints. It expects a 10-digit mobile number and includes
    validation rules like minimum/maximum length and regex pattern.
    """
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}

    if q:
        results.update({"q": q})

    return results


@app.get("/hiddenquery/")
async def read_hidden_query(
    hidden_query: Annotated[
        str | None,
        Query(
            include_in_schema=False,
            description="Test it by running /?hidden_query=Hello",
        ),
    ] = None,
):
    """
    Access a hidden query parameter.

    This endpoint demonstrates query parameters that are excluded from the OpenAPI
    schema. The 'hidden_query' parameter won't appear in the generated documentation
    but can still be used in requests.
    """
    if hidden_query:
        return {"hidden_query": hidden_query}
    else:
        return {"hidden_query": "Not found"}


data = {
    "isbn-9781529046137": "The Hitchhiker's Guide to the Galaxy",
    "imdb-tt0371724": "The Hitchhiker's Guide to the Galaxy",
    "isbn-9781439512982": "Isaac Asimov: The Complete Stories, Vol. 2",
}


def check_valid_id(id: str):
    if not id.startswith(("isbn-", "imdb-")):
        raise ValueError(
            'Invalid ID format, it must start with "isbn-" or "imdb-"'
        )
    return id


@app.get("/customvalidations/")
async def read_custom_items(
    id: Annotated[str | None, AfterValidator(check_valid_id)] = None
):
    """
    Get items with custom validation.

    This endpoint demonstrates custom validation using AfterValidator. It accepts
    an ID that must start with either "isbn-" or "imdb-" and returns corresponding
    item information from a predefined dataset.
    """
    if id:
        item = data.get(id)
    else:
        id, item = random.choice(list(data.items()))

    return {"id": id, "name": item}




class Item(BaseModel):
    name: str
    description: str | None = Field(
        default=None, title="The description of the item", max_length=300
    )
    price: float = Field(gt=0, description="The price must be greater than zero")
    tax: float | None = None


@app.put("/bodyfields/{item_id}")
async def update_item(item_id: int, item: Annotated[Item, Body(embed=True)]):
    """
    Update an item using embedded body fields.

    This endpoint demonstrates the use of Body(embed=True) which wraps the request
    body in an additional JSON object with the model name as the key. The item
    data will be nested under an "item" key in the request body.
    """
    results = {"item_id": item_id, "item": item}
    return results


class Image(BaseModel):
    url: str
    name: str


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()
    image: Image | None = None


@app.put("/nesteditems/{item_id}")
async def update_item(item_id: int, item: Item):
    """
    Update an item with nested models.

    This endpoint demonstrates nested Pydantic models. The Item model includes
    an optional Image sub-model, showing how to handle complex nested data structures
    in request bodies.
    """
    results = {"item_id": item_id, "item": item}
    return results


class Image(BaseModel):
    url: HttpUrl
    name: str


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()
    images: list[Image] | None = None


class Offer(BaseModel):
    name: str
    description: str | None = None
    price: float
    items: list[Item]


@app.post("/offers/")
async def create_offer(offer: Offer):
    """
    Create a new offer with multiple items.

    This endpoint demonstrates deeply nested models. The Offer model contains
    a list of Item models, each of which can have their own nested structures,
    showing how to handle complex hierarchical data.
    """
    return offer

class Image(BaseModel):
    url: HttpUrl
    name: str


@app.post("/images/multiple/")
async def create_multiple_images(images: list[Image]):
    """
    Create multiple images at once.

    This endpoint demonstrates handling lists of models in request bodies.
    It accepts an array of Image objects and returns them, useful for bulk operations.
    """
    return images

@app.post("/index-weights/")
async def create_index_weights(weights: dict[int, float]):
    """
    Create index weights mapping.

    This endpoint demonstrates using dictionaries as request bodies. It accepts
    a dictionary with integer keys and float values, useful for weight mappings
    or indexed configurations.
    """
    return weights


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()


@app.put("/setexample_items/{item_id}")
async def update_item(item_id: int, item: Item):
    """
    Update an item with set-based tags.

    This endpoint demonstrates using sets in Pydantic models. The Item model
    includes a 'tags' field that is a set of strings, which automatically handles
    deduplication and provides set operations.
    """
    results = {"item_id": item_id, "item": item}
    return results


class Image(BaseModel):
    url: HttpUrl
    name: str


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()
    images: list[Image] | None = None


@app.put("/submodel_items/{item_id}")
async def update_item(item_id: int, item: Item):
    """
    Update an item with a list of sub-models.

    This endpoint demonstrates models containing lists of other models. The Item
    includes an optional 'images' field that is a list of Image objects, showing
    how to handle one-to-many relationships in request bodies.
    """
    results = {"item_id": item_id, "item": item}
    return results


@app.get("/cookie/")
async def read_items(ads_id: Annotated[str | None, Cookie()] = None):
    """
    Read items with cookie data.

    This endpoint demonstrates reading HTTP cookies. It extracts the 'ads_id'
    cookie from the request and returns it, showing how to access browser-stored
    data in API endpoints.
    """
    return {"ads_id": ads_id}


@app.get("/headerdemo/")
async def read_items(x_token: Annotated[list[str] | None, Header()] = None):
    """
    Read items with custom headers.

    This endpoint demonstrates reading HTTP headers. It extracts the 'X-Token'
    header (which can have multiple values) and returns them, useful for
    authentication tokens or custom metadata.
    """
    return {"X-Token values": x_token}


@app.post("/responsestatus/", status_code=status.HTTP_201_CREATED)
async def create_item(name: str):
    """
    Create an item with custom response status.

    This endpoint demonstrates setting custom HTTP status codes. It returns
    HTTP 201 Created status instead of the default 200 OK, appropriate for
    resource creation operations.
    """
    return {"name": name}


@app.post("/login/")
async def login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    """
    User login with form data.

    This endpoint demonstrates handling form data instead of JSON. It accepts
    'username' and 'password' as form fields, commonly used for login forms
    and file uploads.
    """
    return {"username": username}


@app.post("/files/")
async def create_file(file: bytes = File()):
    """
    Upload a file.

    This endpoint demonstrates file uploads. It accepts raw file bytes and
    returns the file size, showing how to handle binary data in FastAPI.
    """
    return {"file_size": len(file)}