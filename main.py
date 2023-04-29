from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, RadioField, TextAreaField, SubmitField, SelectMultipleField, SelectField
from wtforms.widgets import CheckboxInput, ListWidget
from wtforms.validators import DataRequired, Length
from sqlalchemy import and_, or_

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my-secret-key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

admin_data = {"training@jalaacademy.com": "jobprogram"}


# Configure Table
class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    mobile_number = db.Column(db.String(10), nullable=False)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    address = db.Column(db.String(50))


# app.app_context().push()
# db.create_all()

class Form(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    mobile_number = StringField("Mobile Number", validators=[DataRequired(), Length(min=10, max=10)])
    date_of_birth = DateField("Date Of Birth", validators=[DataRequired()])
    gender = RadioField("Gender :", choices=["Male", "Female"], default="Male")
    address = TextAreaField("Address")
    country = SelectField("Country", choices=["--Select Country--", "Bangladesh", "Canada", "China", "France",
                                              "India", "Japan", "Nepal", "Sri Lanka", "UK", "USA"])
    # city = SelectField("City", choices=["--Select City--"])
    # country_bangladesh = SelectField("City", choices=["Bogra", "Cox's Bazaar", "Jessore", "Tangail"])
    # country_canada = SelectField("City", choices=["Brant", "Conway", "Hamilton", "North Bay", "Ottawa", "Toronto"])
    # country_china = SelectField("City", choices=["Beijing", "Chizhou", "Hong Kong", "Longhal", "Shangai", "Yumen"])
    # country_france = SelectField("City", choices=["Bron", "Castres", "Lyon", "Paris", "Reims", "Roanne"])
    # country_india = SelectField("City", choices=["Ahmedabad", "Bangalore", "Bhopal", "Chennai", "Delhi", "Kolkata", "Pune"])
    # country_japan = SelectField("City", choices=["Hiroshima", "Nagasaki", "Nagoya", "Yatomi"])
    # country_Nepal = SelectField("City", choices=["Bharatpur", "Damak", "Janakpuri", "Siraha", "Tikapur"])
    # country_srilanka = SelectField("City", choices=["Colombo", "Galle", "Kandy", "Vavuniya"])
    # country_uk = SelectField("City", choices=["Bangor", "Derby", "Perth", "Sunderland"])
    # country_usa = SelectField("City", choices=["California", "Chicago", "Florida", "Hawaii", "New York", "Texas", "Washington"])
    skills = SelectMultipleField(
        'Skills',
        widget=ListWidget(html_tag='ul', prefix_label=False),
        option_widget=CheckboxInput(),
        choices=["AWS", "DevOps", "Full Stack Developer", "Middleware", "QA-Automation", "WebService"])
    save = SubmitField("Save")


class EditForm(Form):
    save = SubmitField("Update")


class SearchForm(FlaskForm):
    name = StringField("Name")
    mobile_number = StringField("Mobile Number")
    search = SubmitField("Search")


@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        pwd = request.form['password']

        if email not in admin_data:
            flash("Invalid Username")
            return redirect(request.url)
        elif admin_data[email] != pwd:
            flash("Invalid Password")
            return redirect(request.url)
        else:
            # admin_data matches
            return redirect(url_for('home'))
    return render_template("login.html")


@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/add-employee", methods=['GET', 'POST'])
def create_employee():
    form = Form()
    if form.validate_on_submit():
        user = User(
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            email=request.form['email'],
            mobile_number=request.form['mobile_number'],
            date_of_birth=datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date(),
            gender=request.form['gender'],
            address=request.form['address'])

        db.session.add(user)
        db.session.commit()

        flash("Successfully added")
        return redirect(url_for('search_employee'))
    return render_template("create_employee.html", form=form)


@app.route("/search", methods=['GET', 'POST'])
def search_employee():
    page = request.args.get('page', 1, type=int)

    employee_list = User.query
    form = SearchForm()

    name = form.name.data or request.args.get('name')
    mobile_number = form.mobile_number.data or request.args.get('mobile_number')

    if name is None and mobile_number is None:
        name = ""
        mobile_number = ""
    elif name is None:
        name = ""
    elif mobile_number is None:
        mobile_number = ""

    if name != "" or mobile_number != "":
        if name is not None or mobile_number is not None:

            employee_list = db.session.query(User).filter(or_(User.first_name == name,
                                                              User.last_name == name, User.mobile_number == mobile_number))
            return render_template("search_employee.html", form=form,
                                   employee_list=employee_list.paginate(page=page, per_page=5, error_out=False),
                                   name=name, mobile_number=mobile_number)

    # if name is not None or mobile_number is not None:
    #     page = 1
    #     if name != "" and mobile_number == "":
    #         emp_name = db.session.query(User).filter(or_(User.first_name == name,
    #                                                      User.last_name == name))
    #         if emp_name.all():
    #             employee_list = emp_name
    #         else:
    #             return render_template("search_employee.html", form=form)
    #
    #     elif name == "" and mobile_number != "":
    #         emp_mobile = db.session.query(User).filter(or_(User.mobile_number == mobile_number))
    #
    #         if emp_mobile.all():
    #             employee_list = emp_mobile
    #         else:
    #             return render_template("search_employee.html", form=form)
    #
    #     elif name != "" and mobile_number != "":
    #         emp_name_mobile = db.session.query(User).filter(and_(or_(User.first_name == name,
    #                                                                  User.last_name == name),
    #                                                              User.mobile_number == mobile_number))
    #         if emp_name_mobile.all():
    #             employee_list = emp_name_mobile
    #         else:
    #             return render_template("search_employee.html", form=form)

    return render_template("search_employee.html", form=form,
                           employee_list=employee_list.paginate(page=page, per_page=5, error_out=False), name=name,
                           mobile_number=mobile_number)


@app.route("/edit/<int:emp_id>", methods=['GET', 'POST'])
def edit_employee(emp_id):
    emp = User.query.get(emp_id)
    edit_form = EditForm(
        first_name=emp.first_name,
        last_name=emp.last_name,
        email=emp.email,
        mobile_number=emp.mobile_number,
        date_of_birth=emp.date_of_birth,
        gender=emp.gender,
        address=emp.address,
    )
    if edit_form.validate_on_submit():
        emp.first_name = edit_form.first_name.data
        emp.last_name = edit_form.last_name.data
        emp.email = edit_form.email.data
        emp.mobile_number = edit_form.mobile_number.data
        emp.date_of_birth = edit_form.date_of_birth.data
        emp.gender = edit_form.gender.data
        emp.address = edit_form.address.data
        db.session.commit()
        return redirect(url_for('search_employee'))
    return render_template("create_employee.html", form=edit_form)


@app.route("/delete/<int:emp_id>", methods=['GET'])
def delete_employee(emp_id):
    emp_to_del = User.query.get(emp_id)
    db.session.delete(emp_to_del)
    db.session.commit()
    return redirect(url_for('search_employee'))


@app.route("/logout")
def logout():
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
