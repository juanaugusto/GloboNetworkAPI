DELETE
######

Deleting list of Network IPv4 asynchronously
********************************************

URL::

    /api/v3/networkv4/async/

You can also delete Network IPv4 objects asynchronously. It is only necessary to provide the same as in the respective synchronous request (For more information please check :ref:`Synchronous Network IPv4 Deleting <url-api-v3-networkv4-delete-delete-list-networkv4s>`). In this case, when you make request NetworkAPI will create a task to fullfil it. You will not receive an empty dict in response as occurs in the synchronous request, but for each Network IPv4 you will receive an identifier for the created task. Since this is an asynchronous request, it may be that Network IPv4 objects have been updated after you receive the response. It is your task, therefore, to consult the API through the available means to verify that your request have been met.

URL Example::

    /api/v3/networkv4/async/

Response body:

.. code-block:: json

    [
        {
            "task_id": [string with 36 characters]
        },...
    ]

Response Example for update of two Network IPv4 objects:

.. code-block:: json

    [
        {
            "task_id": "36dc887e-48bf-4c83-b6f5-281b70976a8f"
        },
        {
            "task_id": "17ebd466-0231-4bd0-8f78-54ed20238fa3"
        }
    ]
