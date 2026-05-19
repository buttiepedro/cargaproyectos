import xmlrpc.client
import os

url = os.getenv("ODOO_URL")
db = os.getenv("ODOO_DB")
username = os.getenv("ODOO_USER")
password = os.getenv("ODOO_PASSWORD")

common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")


def get_projects():
    return models.execute_kw(db, uid, password,
        'project.project', 'search_read',
        [[]],
        {'fields': ['id', 'name']}
    )


def create_task(data, images=None):
    if images is None:
        images = []

    tipo = data['tipo'].capitalize()
    title = f"{tipo} - {data['title'].strip()}"

    tag_ids = models.execute_kw(db, uid, password,
        'project.tags', 'search',
        [[('name', '=', tipo)]]
    )

    description = (
        f"<b>Tipo:</b> {tipo}<br>"
        f"<b>Email:</b> {data['email']}<br><br>"
        f"{data['description']}"
    )

    task_id = models.execute_kw(db, uid, password,
        'project.task', 'create',
        [{
            'name': title,
            'project_id': int(data['project_id']),
            'description': description,
            'tag_ids': [(6, 0, tag_ids)] if tag_ids else []
        }]
    )

    for img in images:
        models.execute_kw(db, uid, password,
            'ir.attachment', 'create',
            [{
                'name': img['filename'],
                'type': 'binary',
                'datas': img['content'],
                'res_model': 'project.task',
                'res_id': task_id,
            }]
        )

    return task_id


def get_tasks_by_email(email):
    task_ids = models.execute_kw(db, uid, password,
        'project.task', 'search',
        [[('description', 'ilike', email)]]
    )

    if not task_ids:
        return []

    tasks = models.execute_kw(db, uid, password,
        'project.task', 'read',
        [task_ids],
        {'fields': ['id', 'name', 'stage_id']}
    )

    messages = models.execute_kw(db, uid, password,
        'mail.message', 'search_read',
        [[
            ('res_model', '=', 'project.task'),
            ('res_id', 'in', task_ids),
            ('message_type', 'in', ['comment', 'email']),
            ('body', '!=', '')
        ]],
        {'fields': ['body', 'date', 'author_id', 'res_id'], 'order': 'date asc'}
    )

    messages_by_task = {}
    for msg in messages:
        tid = msg['res_id']
        messages_by_task.setdefault(tid, []).append({
            'body': msg['body'],
            'date': msg['date'],
            'author': msg['author_id'][1] if msg['author_id'] else 'Desconocido'
        })

    for task in tasks:
        task['stage'] = task['stage_id'][1] if task['stage_id'] else 'Sin estado'
        task['messages'] = messages_by_task.get(task['id'], [])
        del task['stage_id']

    return tasks