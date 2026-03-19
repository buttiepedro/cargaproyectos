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

    # 🎯 título
    title = f"{tipo} - {data['title'].strip()}"

    # 🧠 buscar tag en Odoo
    tag_ids = models.execute_kw(db, uid, password,
        'project.tags', 'search',
        [[('name', '=', tipo)]]
    )

    # 💡 descripción
    description = f"""
    <b>Tipo:</b> {tipo}<br><br>
    {data['description']}
    """

    task_id = models.execute_kw(db, uid, password,
        'project.task', 'create',
        [{
            'name': title,
            'project_id': int(data['project_id']),
            'description': description,
            'tag_ids': [(6, 0, tag_ids)] if tag_ids else []
        }]
    )

    # 📎 imágenes
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