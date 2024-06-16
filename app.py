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
    return render_template('index2.html', patients=data)


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
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO patients (name, email, phone) VALUES (%s, %s, %s)", (name, email, phone))
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
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE patients
            SET name=%s, email=%s, phone=%s
            WHERE id=%s
        """, (name, email, phone, id_data))
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
        cur.execute("""
            UPDATE patients
            SET name=%s, email=%s, phone=%s
            WHERE id=%s
        """, (name, email, phone, id_data))
        mysql.connection.commit()
        flash("Data Updated Successfully")
        return redirect(url_for('Index'))



# view patient
@app.route('/view_patient/<int:patient_id>')
def view_patient(patient_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch patient details
    cur.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
    patient = cur.fetchone()  # Fetch the single patient row as a dictionary

    if not patient:
        flash("Patient not found")
        return redirect(url_for('Index'))

    # Fetch records associated with the patient
    cur.execute("SELECT * FROM records WHERE patient_id = %s", (patient_id,))
    records = cur.fetchall()

    # Fetch admission details associated with the patient
    cur.execute("SELECT * FROM admission_details WHERE patient_id = %s", (patient_id,))
    admissions = cur.fetchall()

    cur.close()

    # Render the view_patient.html template with patient, records, and admissions data
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




if __name__ == "__main__":
    app.run(debug=True)
