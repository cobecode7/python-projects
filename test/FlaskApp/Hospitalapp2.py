from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from wtforms import SelectField
from flask_admin.form import FileUploadField
from markupsafe import Markup
from wtforms.validators import DataRequired
from wtforms_sqlalchemy.fields import QuerySelectField
import os
from wtforms import IntegerField, StringField
app = Flask(__name__)
from flask_admin import BaseView, expose
from flask import Flask, request
from flask import redirect

# Config: update username, password, dbname, host to match your MySQL setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/hospitaldb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'some_secret_key'

db = SQLAlchemy(app)

# Define Patient model to match your table
class Patient(db.Model):
    __tablename__ = 'patient'
    
    PatientID = db.Column(db.Integer, primary_key=True)
    FullName = db.Column(db.String(100))
    DateOfBirth = db.Column(db.Date)
    Gender = db.Column(db.String(10))
    Phone = db.Column(db.String(20))
    Photo = db.Column(db.String(255))
    Document = db.Column(db.String(255))

    def __repr__(self):
        return f'<Patient {self.FullName}>'
class PatientAdmin(ModelView):
    form_columns = ("PatientID","FullName", "DateOfBirth", "Gender", "Phone", "Photo", "Document")

    # Override field types
    form_overrides = {
        "Gender": SelectField,
        "Photo": FileUploadField,
        "Document": FileUploadField,
    }

    # Field arguments
    form_args = {
        "Gender": {
            "choices": [("Male", "Male"), ("Female", "Female")]
        },
        "Photo": {
            "label": "Patient Photo",
            "base_path": os.path.join(os.path.dirname(__file__), "static/uploads/images"),
            "allow_overwrite": False
        },
        "Document": {
            "label": "Patient Document",
            "base_path": os.path.join(os.path.dirname(__file__), "static/uploads/files"),
            "allow_overwrite": False
        }
    }

    # Display thumbnail and link in list view
    column_formatters = {
        "Photo": lambda v, c, m, p: Markup(
            f'<img src="/static/uploads/images/{m.Photo}" width="80">' if m.Photo else ""
        ),
        "Document": lambda v, c, m, p: Markup(
            f'<a href="/static/uploads/files/{m.Document}" target="_blank">{m.Document}</a>'
            if m.Document else ""
        ),
    }
# --- Department model ---
class Department(db.Model):
    __tablename__ = 'department'
    
    DepartmentID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Floor = db.Column(db.Integer)

    # relationship: one department has many doctors
    doctors = db.relationship("Doctor", back_populates="department")

    def __repr__(self):
        return f"<Department {self.Name}>"
# --- Department Admin ---
class DepartmentAdmin(ModelView):
    form_columns = ("DepartmentID","Name", "Floor")  # Include the Floor field
###############################################################
# --- Doctor model ---

class Doctor(db.Model):
    __tablename__ = 'doctor'
    
    DoctorID = db.Column(db.Integer, primary_key=True)
    FullName = db.Column(db.String(100))
    Specialty = db.Column(db.String(100))

    DepartmentID = db.Column(db.Integer, db.ForeignKey("department.DepartmentID"))
    department = db.relationship("Department", back_populates="doctors")

    def __repr__(self):
        return f"<Doctor {self.FullName}>"
 # --- Doctor Admin ---

class DoctorAdmin(ModelView):
    # Show DoctorID in the form
    form_columns = ("DoctorID", "FullName", "Specialty", "department")

    # Optional: Customize labels
    column_labels = {
        "DoctorID": "Doctor ID",
        "FullName": "Full Name",
        "Specialty": "Specialty",
        "department": "Department",
    }

    # Use QuerySelectField for department relation
    def scaffold_form(self):
        form_class = super(DoctorAdmin, self).scaffold_form()
        form_class.department = QuerySelectField(
            "Department",
            query_factory=lambda: Department.query.all(),
            allow_blank=False,
            get_label="Name",
            validators=[DataRequired(message="Please select a department")]
        )
        return form_class

########################################################################################

class Ward(db.Model):
    __tablename__ = "ward"

    WardNumber = db.Column(db.Integer, primary_key=True)
    Type = db.Column(db.String(50))
    Capacity = db.Column(db.Integer)

    def __repr__(self):
        return f"<Ward {self.WardNumber} - {self.Type}>"
class WardAdmin(ModelView):
    form_columns = ["WardNumber", "Type", "Capacity"]
    column_list = ["WardNumber", "Type", "Capacity"]
    column_labels = {
        "WardNumber": "Ward #",
        "Type": "Ward Type",
        "Capacity": "Capacity (Beds)"
    }

    form_overrides = {
        "WardNumber": IntegerField,
        "Type": StringField,
        "Capacity": IntegerField,
    }


########################################################################
class Admission(db.Model):
    __tablename__ = "admission"

    AdmissionID = db.Column(db.Integer, primary_key=True)
    PatientID = db.Column(db.Integer, db.ForeignKey("patient.PatientID"), nullable=False)
    WardNumber = db.Column(db.Integer, db.ForeignKey("ward.WardNumber"), nullable=False)
    AdmitDate = db.Column(db.Date, nullable=False)
    DischargeDate = db.Column(db.Date, nullable=True)

    # Relationships
    patient = db.relationship("Patient", backref="admissions")
    ward = db.relationship("Ward", backref="admissions")

 
    def __repr__(self):
        return f"<Admission {self.AdmissionID}: Patient {self.patient.FullName} in Ward {self.ward.WardNumber}>"
class AdmissionAdmin(ModelView):
    form_columns = ("AdmissionID", "AdmitDate", "DischargeDate")

    column_labels = {
        "AdmissionID": "Admission ID",
        "PatientID": "Patient",
        "WardNumber": "Ward",
        "AdmitDate": "Admit Date",
        "DischargeDate": "Discharge Date"
    }
  #  column_list = ["AdmissionID", "patient", "ward", "AdmitDate", "DischargeDate"]

    column_formatters = {
        "patient": lambda v, c, m, p: m.patient.FullName if m.patient else "",
        "ward": lambda v, c, m, p: str(m.ward.WardNumber) if m.ward else ""
    }
    def scaffold_form(self):
        form_class = super(AdmissionAdmin, self).scaffold_form()
        form_class.patient = QuerySelectField(
            "Patient",
            query_factory=lambda: Patient.query.all(),
            get_label="FullName",
            allow_blank=False,
            validators=[DataRequired(message="Please select a patient")]
        )
        form_class.ward = QuerySelectField(
            "Ward",
            query_factory=lambda: Ward.query.all(),
            get_label="WardNumber",
            allow_blank=False,
            validators=[DataRequired(message="Please select a ward")]
        )
        return form_class
###################################################################################################################




class ReportView(BaseView):
    @expose('/', methods=['GET'])
    def index(self):
        wards = Ward.query.all()
        selected_ward = None
        patients = []

        # Check if a ward is selected via GET parameter
        ward_number = request.args.get('ward')
        if ward_number:
            selected_ward = int(ward_number)
            patients = (
                Patient.query
                .join(Admission)
                .filter(Admission.WardNumber == selected_ward)
                .all()
            )
##################################################################
 # ---- Department and doctor section ----
        departments = Department.query.all()
        selected_department = request.args.get("department", type=int)
        doctors = []

        if selected_department:
            doctors = (
                db.session.query(Doctor)
                .filter(Doctor.DepartmentID == selected_department)
                .all()
            )

        return self.render(
            'admin/reports.html',
            wards=wards,
            patients=patients,
            selected_ward=selected_ward,
            departments=departments,
            doctors=doctors,
            selected_department=selected_department
        )



#################################################################################################

# Flask-Admin setup
admin = Admin(app, name='Hospital Admin', template_mode='bootstrap4')
admin.add_view(PatientAdmin(Patient, db.session))
admin.add_view(DepartmentAdmin(Department, db.session, name="Departments"))
admin.add_view(DoctorAdmin(Doctor, db.session, name="Doctors"))
admin.add_view(WardAdmin(Ward, db.session, name="Wards"))
admin.add_view(AdmissionAdmin(Admission, db.session))
admin.add_view(ReportView(name="Reports", endpoint="reports"))


@app.route("/")
def home():
    return redirect("/admin")
app.run(debug=True)
