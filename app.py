from flask import Flask, render_template, request, url_for, flash,jsonify
from werkzeug.utils import redirect
from flask_mysqldb import MySQL
import MySQLdb
import validators
import json
app = Flask(__name__)
app.secret_key = 'many random bytes'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'crud'

mysql = MySQL(app)

@app.route('/')
def Index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Article ORDER BY Author")  
    data = cur.fetchall()
    cur.close()

    return render_template('index.html', Article=data)

@app.route('/ioc_info_ip_count', methods=['GET'])
def ioc_info_ip_count():
    cur = mysql.connection.cursor()
    cur.execute("SELECT IOC, COUNT(*) as count FROM Article WHERE IOCT = 'IP' GROUP BY IOC")
    data = cur.fetchall()
    cur.close()
    return jsonify(data)

@app.route('/ioc_info_url_count', methods=['GET'])
def ioc_info_url_count():
    cur = mysql.connection.cursor()
    cur.execute("SELECT IOC, COUNT(*) as count FROM Article WHERE IOCT = 'URL' GROUP BY IOC")
    data = cur.fetchall()
    cur.close()
    return jsonify(data)

@app.route('/ioc_info_domain_count', methods=['GET'])
def ioc_info_domain_count():
    cur = mysql.connection.cursor()
    cur.execute("SELECT IOC, COUNT(*) as count FROM Article WHERE IOCT = 'Domain' GROUP BY IOC")
    data = cur.fetchall()
    cur.close()
    return jsonify(data)

@app.route('/ioc_info_hash_count', methods=['GET'])
def ioc_info_hash_count():
    cur = mysql.connection.cursor()
    cur.execute("SELECT IOC, COUNT(*) as count FROM Article WHERE IOCT = 'Hash' GROUP BY IOC")
    data = cur.fetchall()
    cur.close()
    return jsonify(data)


@app.route('/ioc_count')
def ioc_count():
    cur = mysql.connection.cursor()

    cur.execute("SELECT IOCT, COUNT(*) as count FROM Article GROUP BY IOCT")
    data = cur.fetchall()
    cur.close()

    ioc_count_data = [{'IOCT': row[0], 'count': row[1]} for row in data]

    return jsonify(ioc_count_data)










@app.route('/livesearch', methods=['POST'])
def search():
    searchbox = request.form.get("text")
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM Article WHERE Title LIKE %s OR Author LIKE %s OR Source LIKE %s OR IOCT LIKE %s OR IOC LIKE %s OR AG LIKE %s OR Vulnerabilities LIKE %s"
    params = tuple(f'%{searchbox}%' for _ in range(7))
    cursor.execute(query, params)
    columns = [col[0] for col in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    cursor.close()
    return jsonify(results)


"""
@app.route('/', methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        info = request.form['info']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * from Article WHERE Title LIKE %s OR Author LIKE %s OR Source LIKE %s OR IOC LIKE %s OR AG LIKE %s OR Vulnerabilities LIKE %s ", (info, info, info, info, info, info))
        mysql.connection.commit()
        data = cur.fetchall()
        if len(data) == 0 and info == 'all': 
            cur.execute("SELECT * from Article")
            mysql.connection.commit()
            data = cur.fetchall()
        return render_template('index.html', stuff=data)
    return render_template('index.html')
"""
def validate_ip(s):
    a = s.split('.')
    if len(a) != 4:
        return False
    for x in a:
        if not x.isdigit():
            return False
        i = int(x)
        if i < 0 or i > 255:
            return False
    return True






@app.route('/insert', methods = ['POST'])
def insert():
    if request.method == "POST":
        flash("Data Inserted Successfully")
        Title = request.form['Title']
        Author = request.form['Author']
        Source = request.form['Source']
        ioct_types = request.form.getlist('IOCT')  
        ioc_info = request.form['IOC'].split(',')  
        AG = request.form['AG']
        Vulnerabilities = request.form['Vulnerabilities']

        cur = mysql.connection.cursor()

        for ioct_type, ioc in zip(ioct_types, ioc_info):
            if ioct_type == "URL" and validators.url(ioc):
                cur.execute("INSERT INTO Article (Title, Author, Source, IOCT, IOC, AG, Vulnerabilities) VALUES (%s, %s, %s, %s, %s, %s, %s)", (Title, Author, Source, ioct_type, ioc, AG, Vulnerabilities))
            elif ioct_type == "IP" and validate_ip(ioc):
                cur.execute("INSERT INTO Article (Title, Author, Source, IOCT, IOC, AG, Vulnerabilities) VALUES (%s, %s, %s, %s, %s, %s, %s)", (Title, Author, Source, ioct_type, ioc, AG, Vulnerabilities))
        else:
            cur.execute("INSERT INTO Article (Title, Author, Source, IOCT, IOC, AG, Vulnerabilities) VALUES (%s, %s, %s, %s, %s, %s, %s)", (Title, Author, Source, ioct_type, ioc, AG, Vulnerabilities))

        mysql.connection.commit()
        return redirect(url_for('Index'))
    

@app.route('/delete/<string:id_data>', methods = ['GET'])
def delete(id_data):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM Article WHERE id=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('Index'))



@app.route('/update', methods= ['POST', 'GET'])
def update():
    if request.method == 'POST':
        id_data = request.form['id']
        Title = request.form['Title']
        Author = request.form['Author']
        Source = request.form['Source']
        IOCT = request.form['IOCT']
        IOC = request.form['IOC']
        AG = request.form['AG']
        Vulnerabilities = request.form['Vulnerabilities']

        cur = mysql.connection.cursor()

        if IOCT in ["URL", "IP"]:
            IOC_list = [ioc.strip() for ioc in IOC.split(',')]
            IOC_values = ','.join([f"'{ioc}'" for ioc in IOC_list])
            cur.execute(f"UPDATE Article SET Title = %s, Author = %s, Source = %s, IOCT = %s, IOC = {IOC_values}, AG = %s, Vulnerabilities = %s WHERE id = %s", (Title, Author, Source, IOCT, AG, Vulnerabilities, id_data))
        else:
            cur.execute("UPDATE Article SET Title = %s, Author = %s, Source = %s, IOCT = %s, IOC = %s, AG = %s, Vulnerabilities = %s WHERE id = %s", (Title, Author, Source, IOCT, IOC, AG, Vulnerabilities, id_data))

        flash("Data Updated Successfully")
        mysql.connection.commit()
        return redirect(url_for('Index'))


@app.route('/related_articles/<int:article_id>', methods=['GET'])
def related_articles(article_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Article WHERE id != %s AND (Author = (SELECT Author FROM Article WHERE id = %s) OR Title = (SELECT Title FROM Article WHERE id = %s) OR Source = (SELECT Source FROM Article WHERE id = %s) OR AG = (SELECT AG FROM Article WHERE id = %s) OR Vulnerabilities = (SELECT Vulnerabilities FROM Article WHERE id = %s))", (article_id, article_id, article_id, article_id, article_id, article_id))
    data = cur.fetchall()
    cur.close()
    return jsonify(data)





if __name__ == "__main__":
    app.run(debug=True)

