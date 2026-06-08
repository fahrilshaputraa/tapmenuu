from django.shortcuts import render


def page(template_name):
    def view(request):
        return render(request, f'core/pages/{template_name}')

    return view


landing = page('landing.html')
login = page('login.html')
register = page('register.html')
dashboard = page('dashboard.html')
management_menu = page('management-menu.html')
store = page('store.html')
orders = page('orders.html')
employee = page('employee.html')
reports = page('reports.html')
tables = page('tables.html')
book_menu = page('book-menu.html')
