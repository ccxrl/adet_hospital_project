# add:
# address column
# upload picture
# doctor table
# 	- pk doctor id
# 	- fk patient id

# patient table
# 	- fk doctor id

# add_patient.html
# 	- doctor field

# view_patient
# 	- information
# 		- doctor name 




from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = 'secret'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask_crud'

mysql = MySQL(app)


@app.route('/')
def Index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM patients")
    data = cur.fetchall()
    cur.close()
    return render_template('Index.html', patients=data)


@app.route('/add_patient')
def add_patient():
    return render_template('add_patient.html')

# add patient
@app.route('/insert', methods=['POST'])
def insert():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        weight = request.form['weight']
        height = request.form['height']
        blood_type = request.form['blood_type']
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO patients (name, email, phone, address, weight, height, blood_type) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (name, email, phone, address, weight, height, blood_type))
        mysql.connection.commit()
        flash("Data Inserted Successfully")
        return redirect(url_for('Index'))



# delete patient
@app.route('/delete/<string:id_data>', methods=['GET'])
def delete(id_data):
    cur = mysql.connection.cursor()

    # Check if patient has associated records
    cur.execute("SELECT * FROM records WHERE patient_id=%s", (id_data,))
    records = cur.fetchall()

    if records:
        flash("Cannot delete patient because records exist.")
        return redirect(url_for('Index'))

    # Check if patient has associated admission details
    cur.execute("SELECT * FROM admission_details WHERE patient_id=%s", (id_data,))
    admissions = cur.fetchall()

    if admissions:
        flash("Cannot delete patient because admission details exist.")
        return redirect(url_for('Index'))

    # If no records or admission details exist, proceed with deletion
    cur.execute("DELETE FROM patients WHERE id=%s", (id_data,))
    mysql.connection.commit()
    flash("Patient Deleted Successfully")

    cur.close()

    return redirect(url_for('Index'))




# update button patient
@app.route('/update_patient', methods=['POST'])
def update_patient():
    if request.method == 'POST':
        id_data = request.form['id']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        weight = request.form['weight']
        height = request.form['height']
        blood_type = request.form['blood_type']
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE patients
            SET name=%s, email=%s, phone=%s, address=%s, weight=%s, height=%s, blood_type=%s
            WHERE id=%s
        """, (name, email, phone, address, weight, height, blood_type, id_data))
        mysql.connection.commit()
        flash("Data Updated Successfully")
        return redirect(url_for('Index'))


# edit patient
@app.route('/edit_patient/<int:patient_id>', methods=['GET', 'POST'])
def edit_patient(patient_id):
    cur = mysql.connection.cursor()
    if request.method == 'GET':
        cur.execute("SELECT * FROM patients WHERE id=%s", (patient_id,))
        patient = cur.fetchone()
        cur.close()
        if patient:
            return render_template('edit_patient.html', patient=patient)
        else:
            flash("Patient not found")
            return redirect(url_for('Index'))
    elif request.method == 'POST':
        id_data = request.form['id']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        weight = request.form['weight']
        height = request.form['height']
        blood_type = request.form['blood_type']
        cur.execute("""
            UPDATE patients
            SET name=%s, email=%s, phone=%s, address=%s, weight=%s, height=%s, blood_type=%s
            WHERE id=%s
        """, (name, email, phone, address, weight, height, blood_type, id_data))
        mysql.connection.commit()
        flash("Data Updated Successfully")
        return redirect(url_for('Index'))




# view patient
@app.route('/view_patient/<int:patient_id>')
def view_patient(patient_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
    patient = cur.fetchone()

    if not patient:
        flash("Patient not found")
        return redirect(url_for('Index'))

    cur.execute("SELECT * FROM records WHERE patient_id = %s", (patient_id,))
    records = cur.fetchall()

    cur.execute("SELECT * FROM admission_details WHERE patient_id = %s", (patient_id,))
    admissions = cur.fetchall()

    cur.close()

    return render_template('view_patient.html', patient=patient, records=records, admissions=admissions)










# PATIENT RECORDS
# add patient record
@app.route('/add_record/<int:patient_id>', methods=['GET', 'POST'])
def processrecord(patient_id):
    if request.method == 'POST':
        diagnosis = request.form['diagnosis']
        treatment_plan = request.form['treatment_plan']
        date_of_visit = request.form['date_of_visit']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO records (patient_id, diagnosis, treatment_plan, date_of_visit) VALUES (%s, %s, %s, %s)",
                    (patient_id, diagnosis, treatment_plan, date_of_visit))
        mysql.connection.commit()
        flash("Record Added Successfully")
        return redirect(url_for('view_patient', patient_id=patient_id))
    return render_template('add_record.html', patient_id=patient_id)


# edit patient record
@app.route('/edit_record/<int:record_id>', methods=['GET', 'POST'])
def edit_record(record_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        diagnosis = request.form['diagnosis']
        treatment_plan = request.form['treatment_plan']
        date_of_visit = request.form['date_of_visit']
        cur.execute("""
            UPDATE records
            SET diagnosis=%s, treatment_plan=%s, date_of_visit=%s
            WHERE record_id=%s
        """, (diagnosis, treatment_plan, date_of_visit, record_id))
        mysql.connection.commit()
        flash("Record Updated Successfully")
        return redirect(url_for('view_patient', patient_id=request.form['patient_id']))
    else:
        cur.execute("SELECT * FROM records WHERE record_id = %s", (record_id,))
        record = cur.fetchone()
        return render_template('edit_record.html', record=record)


# delete patient record
@app.route('/delete_record/<int:record_id>', methods=['GET'])
def delete_record(record_id):
    cur = mysql.connection.cursor()

    # Fetch patient_id before deleting the record
    cur.execute("SELECT patient_id FROM records WHERE record_id = %s", (record_id,))
    result = cur.fetchone()

    if not result:
        flash("Error: Record not found")
        cur.close()
        return redirect(url_for('Index'))  # Redirect to index if record not found

    patient_id = result[0]  # Access the first element of the tuple

    # Delete the record
    cur.execute("DELETE FROM records WHERE record_id=%s", (record_id,))
    mysql.connection.commit()
    flash("Record Deleted Successfully")

    cur.close()

    # Redirect to view_patient page with the correct patient_id
    return redirect(url_for('view_patient', patient_id=patient_id))









# ADD ADMISSION DETAILS
# add admission details
@app.route('/add_admission/<int:patient_id>', methods=['GET', 'POST'])
def add_admission(patient_id):
    if request.method == 'POST':
        admission_date = request.form['admission_date']
        discharge_date = request.form['discharge_date']
        room_number = request.form['room_number']

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO admission_details (patient_id, admission_date, discharge_date, room_number)
            VALUES (%s, %s, %s, %s)
        """, (patient_id, admission_date, discharge_date, room_number))
        mysql.connection.commit()
        flash("Admission Details Added Successfully")
        return redirect(url_for('view_patient', patient_id=patient_id))

    return render_template('add_admission.html', patient_id=patient_id)


@app.route('/edit_admission/<int:admission_id>', methods=['GET', 'POST'])
def edit_admission(admission_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST':
        # Retrieve data from the form
        admission_date = request.form['admission_date']
        discharge_date = request.form['discharge_date']
        room_number = request.form['room_number']
        patient_id = request.form['patient_id']  # Ensure patient_id is fetched from form

        # Update the admission details in the database
        cur.execute("""
            UPDATE admission_details
            SET admission_date=%s, discharge_date=%s, room_number=%s
            WHERE admission_id=%s
        """, (admission_date, discharge_date, room_number, admission_id))
        mysql.connection.commit()

        flash("Admission Details Updated Successfully", "success")

        # Redirect to view_patient page after successful update
        return redirect(url_for('view_patient', patient_id=patient_id))
    else:
        # Fetch the admission details for editing
        cur.execute("SELECT * FROM admission_details WHERE admission_id = %s", (admission_id,))
        admission = cur.fetchone()

        # Ensure admission data is fetched successfully
        if not admission:
            flash("Error: Admission details not found", "error")
            return redirect(url_for('Index'))  # Redirect to index if admission details not found

        patient_id = admission['patient_id']  # Fetch patient_id from admission details

        cur.close()

        # Pass admission and patient_id to the template context for rendering
        return render_template('edit_admission.html', admission=admission, patient_id=patient_id)






# delete admission details
@app.route('/delete_admission/<int:admission_id>/<int:patient_id>', methods=['GET'])
def delete_admission(admission_id, patient_id):
    cur = mysql.connection.cursor()

    # Delete the admission detail
    cur.execute("DELETE FROM admission_details WHERE admission_id=%s", (admission_id,))
    mysql.connection.commit()
    flash("Admission Details Deleted Successfully")

    cur.close()

    return redirect(url_for('view_patient', patient_id=patient_id))






# DOCTORS

# view doctors
@app.route('/view_doctors')
def view_doctors():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM doctors")
    doctors = cur.fetchall()
    cur.close()
    
    return render_template('doctors.html', doctors=doctors)



# add doctor
@app.route('/add_doctor', methods=['GET', 'POST'])
def insert_doctor():
    if request.method == "POST":
        name = request.form['name']
        specialization = request.form['specialization']
        
        # Insert data into the database
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO doctors (name, specialization)
            VALUES (%s, %s)
        """, (name, specialization))
        mysql.connection.commit()
        flash("Doctor Inserted Successfully")
        
        # Redirect to view_doctors instead of Index
        return redirect(url_for('view_doctors'))

    return render_template('add_doctor.html')



# delete doctor
@app.route('/delete_doctor/<int:doctor_id>', methods=['GET'])
def delete_doctor(doctor_id):
    cur = mysql.connection.cursor()

    # Check if the doctor is assigned to any records
    cur.execute("SELECT * FROM records WHERE doctor_assigned=%s", (doctor_id,))
    records = cur.fetchall()

    if records:
        flash("Cannot delete doctor because records are assigned.")
        return redirect(url_for('index'))

    # Proceed with deleting the doctor if no records are assigned
    cur.execute("DELETE FROM doctors WHERE doctor_id=%s", (doctor_id,))
    mysql.connection.commit()
    flash("Doctor Deleted Successfully")

    cur.close()

    return redirect(url_for('index'))




# update doctor info
@app.route('/update_doctor', methods=['POST'])
def update_doctor():
    if request.method == 'POST':
        doctor_id = request.form['doctor_id']
        name = request.form['name']
        specialization = request.form['specialization']

        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE doctors
            SET name=%s, specialization=%s
            WHERE doctor_id=%s
        """, (name, specialization, doctor_id))
        mysql.connection.commit()
        flash("Doctor Updated Successfully")
        return redirect(url_for('index'))



# edit doctor
@app.route('/edit_doctor/<int:doctor_id>', methods=['GET', 'POST'])
def edit_doctor(doctor_id):
    cur = mysql.connection.cursor()

    if request.method == 'GET':
        cur.execute("SELECT * FROM doctors WHERE doctor_id=%s", (doctor_id,))
        doctor = cur.fetchone()
        cur.close()
        
        if doctor:
            return render_template('edit_doctor.html', doctor=doctor)
        else:
            flash("Doctor not found")
            return redirect(url_for('index'))

    elif request.method == 'POST':
        doctor_id = request.form['doctor_id']
        name = request.form['name']
        specialization = request.form['specialization']

        cur.execute("""
            UPDATE doctors
            SET name=%s, specialization=%s
            WHERE doctor_id=%s
        """, (name, specialization, doctor_id))
        mysql.connection.commit()
        flash("Doctor Updated Successfully")
        return redirect(url_for('index'))









if __name__ == "__main__":
    app.run(debug=True)
