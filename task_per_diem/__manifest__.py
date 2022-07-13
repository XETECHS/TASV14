{
    'name': 'Task per diem',
    'version': '1.0',
    'summary': """n el formulario de “Tareas” agregar la pestaña “Viáticos” que permita seleccionar productos de tipo “Servicio” a utilizar para esa tarea.""",
    'description': """n el formulario de “Tareas” agregar la pestaña “Viáticos” que permita seleccionar productos de tipo “Servicio” a utilizar para esa tarea.""",
    'category': 'Project',
    'author': 'Xetechs S.A',
    'website': 'project',
    'license': '',
    'depends': ['project', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/project_task.xml',
    ],
}