from clock import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    roll = db.Column(db.String, nullable=False)
    password = db.Column(db.Text, nullable=False)
    state = db.Column(db.Integer)

    def __init__(self, username, name, roll, password, state):
        self.username = username
        self.name = name
        self.roll = roll
        self.password = password
        self.state = state

    def __repr__(self):
        return f'<User: {self.username}>'

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    code = db.Column(db.String, nullable=False)
    password = db.Column(db.Text, nullable=False)
    departament = db.Column(db.String)
    company = db.Column(db.String)
    state = db.Column(db.Integer)


    def __init__(self, name, code, password, departament, company, state):
        self.name = name
        self.code = code
        self.password = password
        self.departament = departament
        self.company = company
        self.state = state

    def __repr__(self):
        return f'<Employee: {self.name}>'
    
class RegisterDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    employee = db.relationship('Employee', backref='Empleados')
    register_datetime = db.Column(db.DateTime)
    register_date = db.Column(db.Date)
    in_hour = db.Column(db.String)
    lunch_start = db.Column(db.String)
    lunch_end = db.Column(db.String)
    out_hour = db.Column(db.String)
    register_no_day = db.Column(db.Integer)
    register_day = db.Column(db.String)


    def __init__(self, employee_id, register_datetime, register_date, in_hour, lunch_start, lunch_end, out_hour, register_no_day, register_day):
        self.employee_id = employee_id
        self.register_datetime = register_datetime
        self.register_date = register_date
        self.in_hour = in_hour
        self.lunch_start = lunch_start
        self.lunch_end = lunch_end
        self.out_hour = out_hour
        self.register_no_day = register_no_day
        self.register_day = register_day

    def __repr__(self):
        return f'<Employee: {self.employee_id}>'