from flask import Flask, request, jsonify, render_template, redirect, url_for ,flash,session
import psycopg2
from datetime import datetime

app = Flask(__name__)
@app.route("/")  # الصفحة الرئيسية
def home():
    return render_template("login.html")  # استخدام ملف معين كصفحة رئيسية
# Database connection
try:
    conn = psycopg2.connect(
        dbname='test',  # Change this to your actual database name
        user='postgres',
        password='esraa1154',
        host='localhost',
        port="5432"
    )
except psycopg2.Error as e:
    print(f"Database connection failed: {e}")
    exit()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            return render_template('login.html', message="Enter Your Email Please!")

        try:
            cur = conn.cursor()
            query = "SELECT * FROM \"users\" WHERE \"Email\" = %s AND \"Password\" = %s"
            cur.execute(query, (email, password))
            user = cur.fetchone()
            cur.close()

            if user:
                # تمرير البريد الإلكتروني كـ query parameter
                return redirect(url_for('choose_project', user_email=email))
            else:
                return render_template('login.html', message="البريد الإلكتروني أو كلمة المرور غير صحيحة!")
        
        except Exception as e:
            return f"حدث خطأ: {e}"

    return render_template('login.html')


############################project

# اختيار المشروع
@app.route('/choose_project', methods=['GET', 'POST'])
def choose_project():
    if request.method == 'POST':
            # تمرير المشروع إلى صفحة اختيار القسم
            return redirect(url_for('choose_dep'))
    return render_template('project.html')

# اختيار القسم
@app.route('/choose_dep', methods=['GET', 'POST'])
def choose_dep():
    project = request.args.get('project')  # استلام المشروع من الرابط
    if request.method == 'POST':
            # تمرير المشروع والقسم إلى صفحة اختيار الـ sheet
            return redirect(url_for('choose_sheet'))
    return render_template('department.html')

# اختيار الـ sheet
@app.route('/choose_sheet', methods=['GET', 'POST'])
def choose_sheet():
    project = request.args.get('project')  # استلام المشروع من الرابط
    department = request.args.get('department')  # استلام القسم من الرابط
    if request.method == 'POST':
        sheet = request.form.get('sheet')  # استلام الـ sheet
        if sheet:
            # تمرير المشروع والقسم والـ sheet إلى لوحة التحكم
            return redirect(url_for('dashboard', project=project, department=department, sheet=sheet))
    return render_template('sheet.html', project=project, department=department)

# لوحة التحكم
@app.route('/dashboard')
def dashboard():
    project = request.args.get('project')  # استلام المشروع من الرابط
    department = request.args.get('department')  # استلام القسم من الرابط
    sheet = request.args.get('sheet')  # استلام الـ sheet من الرابط
    return render_template('dashboard.html', project=project, department=department, sheet=sheet)

current_serial=7610
@app.route('/input_page', methods=['GET', 'POST'])
def input_page():
    global current_serial

    if request.method == 'POST':
        # Fetching data from the form
        data = request.form.to_dict()

        # Extracting "الشهر" and "السنة" from "تاريخ السداد"
        date = data.get('تاريخ السداد')
        if date:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            data['الشهر'] = date_obj.month
            data['السنه'] = date_obj.year

        # Generating a unique ID
        current_serial += 1
        data['id'] = f"AP{current_serial}"

        # Pass the data to the confirmation page
        return render_template('confirm.html', 
                       نوع_المستند=data['نوع المستند'], 
                       رقم_القيد=data['رقم القيد'],
                       رقم_الايصال=data['رقم الايصال'],
                       تاريخ_السداد=data['تاريخ السداد'],
                       قيمة_السداد=data['قيمة السداد'],
                       التوجيه=data['التوجيه'],
                       كود_الحساب=data['كود الحساب'],
                       إسم_الحساب=data['إسم الحساب'],
                       البيان=data['البيان'],
                       رقم_الشيك=data['رقم الشيك'],
                       تاريخ_الاستحقاق=data['تاريخ الاستحقاق'],
                       البنك=data['البنك'],
                       كود_المورد=data['كود المورد'],
                       اسم_المورد=data['اسم المورد'],
                       كود_العميل=data['كود العميل'],
                       اسم_العميل=data['اسم العميل'],
                       رقم_العقد=data['رقم العقد'],
                       رقم_القسط=data['رقم القسط'],
                       الشهر=data['الشهر'],
                       السنة=data['السنه'],
                       id=data['id'],
                       كود_الوحدة=data['كود الوحدة'],
                       رقم_الفاتورة=data['رقم الفاتورة'],
                       تاريخ_القسط=data['تاريخ القسط'],
                       نوع_القسط=data['نوع القسط'],
                       قيمة_القسط=data['قيمة القسط'])


    return render_template('ap_data.html')

@app.route('/submit_input', methods=['POST'])
def submit_input():
    data = request.form.to_dict()

    # التحقق من وجود الـ ID بالفعل في قاعدة البيانات
    def generate_unique_id():
        global current_serial
        cur = conn.cursor()
        while True:
            current_serial += 1
            new_id = f"AP{current_serial}"
            cur.execute('SELECT COUNT(*) FROM AP WHERE id = %s', (new_id,))
            count = cur.fetchone()[0]
            if count == 0:  # إذا كان الـ ID غير موجود
                cur.close()
                return new_id

    # توليد ID جديد
    if not data.get('id'):
        data['id'] = generate_unique_id()

    # إدخال البيانات في قاعدة البيانات
    try:
        cur = conn.cursor()
        query = """
            INSERT INTO AP (
                    "نوع المستند", 
                    "رقم القيد", 
                    "رقم الايصال", 
                    "تاريخ السداد", 
                    "قيمة السداد", 
                    "التوجيه", 
                    "كود الحساب", 
                    "إسم الحساب", 
                    "البيان", 
                    "رقم الشيك", 
                    "تاريخ الاستحقاق", 
                    "البنك", 
                    "كود المورد", 
                    "اسم المورد", 
                    "كود العميل", 
                    "اسم العميل", 
                    "رقم العقد", 
                    "رقم القسط", 
                    "الشهر", 
                    "السنة", 
                    "id",
                    "كود الوحدة", 
                    "رقم الفاتورة", 
                    "تاريخ القسط",
                    "نوع القسط",
                    "قيمة القسط"
                ) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)                   
        """
        values = (
            data['نوع المستند'], data['رقم القيد'], data['رقم الايصال'], data['تاريخ السداد'], data['قيمة السداد'],
            data['التوجيه'], data['كود الحساب'], data['إسم الحساب'], data['البيان'],
            data['رقم الشيك'], data['تاريخ الاستحقاق'], data['البنك'], data['كود المورد'],
            data['اسم المورد'], data['كود العميل'], data['اسم العميل'], data['رقم العقد'],
            data['رقم القسط'], data['الشهر'], data['السنه'], data['id'], data['كود الوحدة'], data['رقم الفاتورة'], data['تاريخ القسط'],
            data['نوع القسط'], data['قيمة القسط']
        )
        cur.execute(query, values)
        conn.commit()
        cur.close()

        return render_template('ap_data.html', success_message="تم إدخال البيانات بنجاح")
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400



    except Exception as e:
        conn.rollback()
        return f"Database Error: {e}"
 
    
@app.route('/filter_page', methods=['GET'])
def filter_page():
    return render_template('Filter_page.html')

@app.route('/filter_data', methods=['POST'])
def filter_data():
    try:
        column_name = request.form['column_name']
        filter_value = request.form['filter_value']
        cur = conn.cursor()
        query = f'SELECT * FROM ap WHERE "{column_name}" = %s'
        cur.execute(query, (filter_value,))
        entries = cur.fetchall()
        cur.close()

        return render_template('show_data.html', data=entries)
    
    except Exception as e:
        return f"حدث خطأ أثناء جلب البيانات المفلترة: {e}"

@app.route('/view_all_data', methods=['GET'])
def view_all_data():
    try:
        cur = conn.cursor()
        query = 'SELECT * FROM ap '
        cur.execute(query)
        entries = cur.fetchall()
        cur.close()

        return render_template('show_data.html', data=entries)

    
    except Exception as e:
        return f"حدث خطأ أثناء جلب البيانات: {e}"

@app.route('/query_page', methods=['GET'])
def query_page():
    return render_template('query_page.html')

@app.route('/execute_query', methods=['POST'])
def execute_query():
    try:
        query = request.form['query']
        cur = conn.cursor()
        cur.execute(query)
        if query.strip().lower().startswith('select'):
            entries = cur.fetchall()
            cur.close()
            return render_template('show_data.html', data=entries)
        else:
            conn.commit()
            cur.close()
            return "تم تنفيذ الاستعلام بنجاح."
    
    except Exception as e:
        return f"حدث خطأ أثناء تنفيذ الاستعلام: {e}"

@app.route('/edit/<string:entry_id>', methods=['GET'])
def edit_entry(entry_id):
    try:
        cur = conn.cursor()
        query = """
            SELECT 
                "نوع المستند", "رقم القيد", "رقم الايصال", "تاريخ السداد", 
                "قيمة السداد", "التوجيه", "كود الحساب", "إسم الحساب", 
                "البيان", "رقم الشيك", "تاريخ الاستحقاق", "البنك", 
                "كود المورد", "اسم المورد", "كود العميل", "اسم العميل", 
                "رقم العقد", "رقم القسط", "الشهر", "السنة", "id",
                "كود الوحدة", "رقم الفاتورة", "تاريخ القسط", "نوع القسط", "قيمة القسط"
            FROM ap 
            WHERE id = %s
        """
        cur.execute(query, (entry_id,))
        row = cur.fetchone()
        cur.close()

        if row:
            columns = [
                "نوع المستند", "رقم القيد", "رقم الايصال", "تاريخ السداد", 
                "قيمة السداد", "التوجيه", "كود الحساب", "إسم الحساب", 
                "البيان", "رقم الشيك", "تاريخ الاستحقاق", "البنك", 
                "كود المورد", "اسم المورد", "كود العميل", "اسم العميل", 
                "رقم العقد", "رقم القسط", "الشهر", "السنة", "id",
                "كود الوحدة", "رقم الفاتورة", "تاريخ القسط", "نوع القسط", "قيمة القسط"
            ]
            entry = dict(zip(columns, row))
            return render_template('edit_entry.html', entry=entry)
        else:
            return "لم يتم العثور على البيانات", 404

    except Exception as e:
        return f"حدث خطأ: {e}", 500

from datetime import datetime
from flask import request, redirect, url_for

@app.route('/edit/<string:entry_id>', methods=['POST'])
def update_entry(entry_id):
    try:
        # Retrieve the updated data from the form
        data = request.form.to_dict()

        # حساب "الشهر" و"السنة" من "تاريخ السداد"
        payment_date = data.get('تاريخ السداد')
        if payment_date:
            date_obj = datetime.strptime(payment_date, '%Y-%m-%d')
            data['الشهر'] = str(date_obj.month)  # حفظ الشهر كـ string
            data['السنة'] = str(date_obj.year)  # حفظ السنة كـ string

        # إعداد الحقول والقيم للتحديث
        update_fields = []
        values = []
        for key, value in data.items():
            if key != 'id':  # تجاهل حقل ID
                # التعامل مع القيم الفارغة
                if value == "None" or value == "":
                    update_fields.append(f'"{key}" = NULL')  # الحقول الفارغة تصبح NULL
                else:
                    update_fields.append(f'"{key}" = %s')  # إضافة الحقول والقيم
                    values.append(value)

        # إضافة ID إلى القيم لتحديد السجل في شرط WHERE
        values.append(entry_id)

        # إنشاء استعلام التحديث
        update_query = f"""
            UPDATE ap 
            SET {", ".join(update_fields)} 
            WHERE id = %s
        """

        # تنفيذ استعلام التحديث
        cur = conn.cursor()
        cur.execute(update_query, values)
        conn.commit()
        cur.close()

        # إعادة التوجيه إلى صفحة عرض البيانات
        return redirect(url_for('view_all_data'))

    except Exception as e:
        conn.rollback()
        return f"حدث خطأ أثناء تحديث البيانات: {e}", 500


################################################delete###############################################################3
@app.route('/confirm_delete/<string:entry_id>', methods=['GET'])
def confirm_delete(entry_id):
    try:
        with conn.cursor() as cur:
            query = 'SELECT * FROM ap WHERE "id" = %s'
            cur.execute(query, (entry_id,))
            record = cur.fetchone()

        if record:
            return render_template('delete_data.html', data=record)
        else:
            flash("السجل غير موجود", "warning")
            return redirect(url_for('view_all_data'))
    except Exception as e:
        flash(f"حدث خطأ أثناء جلب البيانات: {e}", "danger")
        return redirect(url_for('view_all_data'))


@app.route('/delete_entry/<string:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    try:
        with conn.cursor() as cur:
            query = 'DELETE  FROM ap WHERE "id" = %s'
            cur.execute(query, (entry_id,))
            conn.commit()
        return redirect(url_for('view_all_data'))
    except Exception as e:
        return f"حدث خطأ أثناء حذف البيانات: {e}"

###########################################dep


if __name__ == '__main__':
    app.run(debug=True)