from flask import Blueprint, render_template, request, url_for
import datetime
import time
from clock.auth import login_required

from .models import RegisterDetail, Employee
from clock import db

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route('/', methods=('GET', 'POST'))
@login_required
def dashboard():
    empresas = ["VW Partes", "Repasa", "Autoluz"]
    registerdetail = RegisterDetail.query.all()
    employees = Employee.query.all()
    
    if request.method == 'POST':
        company = request.form['company']
        employee = request.form['employee']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        
        register_filter = RegisterDetail.query.join(Employee).filter(
            RegisterDetail.register_date.between(start_date, end_date),
            RegisterDetail.employee_id==employee,
            Employee.company==company
        ).all()
        return render_template('dashboard.html', registerdetail=register_filter, employees=employees, empresas=empresas)

    
    return render_template('dashboard.html', registerdetail=registerdetail, employees=employees, empresas=empresas)
