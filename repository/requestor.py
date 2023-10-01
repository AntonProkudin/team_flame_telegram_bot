import json

import requests


class Requestor:

    def __init__(self):
        self.url = 'https://api.teamflame.ru'
        self.access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImFydGVtLnNoaXB1bm92MTk5NUBnbWFpbC5jb20iLCJ1c2VySWQiOiI2NTEwODE5MTg3OTk4MmMyMGYwOTlkZGQiLCJpYXQiOjE2OTYxMTcyMTMsImV4cCI6MTY5NjQxNzIxM30.qwbhK5SKzYH-vKSjPkFauZ6rIHR4vFJG3sEdN50paiM'

        self.headers = {'Authorization': f'Bearer',
                        'Content-Type': 'application/json; charset=utf-8'}

    def set_header(self, access_token):
        self.headers = {'Authorization': f'Bearer {access_token}',
                        'Content-Type': 'application/json'}

    def get_user_task(self):
        response = requests.get(f'{self.url}/task/my', headers=self.headers)

        return response.json()

    def get_task_by_id(self, task_id):
        response = requests.get(f'{self.url}/task/{task_id}', headers=self.headers)

        return response.json()

    # Получить статусы по борду
    def get_column_by_board_id(self, board_id):
        return requests.get(f'{self.url}/column/getByBoard/{board_id}', headers=self.headers).json()

    def change_task_status(self, task_id, column_id):
        task = self.get_task_by_id(task_id)

        response = requests.post(f'{self.url}/task/change-column/{task_id}', json.dumps({
            'columnId': column_id, 'location': task['spaceId'],
        }), headers=self.headers)

        return response.json()

    def create_comment(self, comment_description, task_id):
        return requests.post(f'{self.url}/comment/create', json.dumps({
            'task': task_id,
            'text': comment_description
        }), headers=self.headers).json()

    def update_task(self, task_id, field, value):
        task = self.get_task_by_id(task_id)

        task[field] = value

        response = requests.post(f'{self.url}/task/update/{task_id}', data=json.dumps(task), headers=self.headers)

        return response.json()

    def get_user_boards(self):
        return requests.get(f'{self.url}/board/boardsByUser', headers=self.headers).json()

    def get_current_user(self):
        return requests.get(f'{self.url}/user/me', headers=self.headers).json()

    def create_task(self, title, description):
        # board_id, column_id, location, project_id, space_id

        board = self.get_user_boards()[0]

        board_id = board['id']
        space_id = board['spaceId']
        project_id = board['projectId']
        column_id = board['columns'][0]

        response = requests.post(f'{self.url}/task/create', headers=self.headers, data=json.dumps({
            'name': title,
            'description': description, 'boardId': board_id, 'spaceId': space_id, 'projectId': project_id,
            'columnId': column_id, 'location': space_id, 'users': [self.get_current_user()['id']]
        }))

        return response.json()

    def authorize_user(self, email, password):
        print(json.dumps({'email': email, 'password': password}))

        response = requests.post('https://auth-api.teamflame.ru/auth/sign-in',
                                 json.dumps({'email': email, 'password': password}),
                                 headers={'Content-Type': 'application/json'})

        return response
