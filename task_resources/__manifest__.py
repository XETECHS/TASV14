{
    'name': 'Task resources',
    'version': '1.0',
    'summary': """En el formulario de “Tareas” agregar la pestaña 'Recursos' que permita seleccionar los productos a utilizar para esa tarea.
                Los campos a mostrar en esa vista son los siguientes: Referencia interna, nombre, unidad de medida, cantidad, costo y subtotal.""",
    'description': """En el formulario de “Tareas” agregar la pestaña 'Recursos' que permita seleccionar los productos a utilizar para esa tarea.
                Los campos a mostrar en esa vista son los siguientes: Referencia interna, nombre, unidad de medida, cantidad, costo y subtotal.""",
    'category': 'Project',
    'author': 'Xetechs S.A',
    'website': 'project',
    'license': '',
    'depends': ['project', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'views/project_task.xml',
    ],
}