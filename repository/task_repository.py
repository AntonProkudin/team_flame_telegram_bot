import requests

url = "https://jsonplaceholder.typicode.com/posts/1"


class TaskRepository:

    def getAllTasks(self):
        return requests.get(f'{url}/tasks').json()
