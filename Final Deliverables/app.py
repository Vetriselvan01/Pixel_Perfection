from flask import Flask, render_template, request, redirect, url_for, session
import ibm_db
import ibm_boto3
import requests
from ibm_botocore.client import Config
import io
app = Flask(__name__)
app.secret_key = 'ffiniaduioretggefee'
conn = ibm_db.connect("DATABASE=bludb; HOSTNAME=19af6446-6171-4641-8aba-9dcff8e1b6ff.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud; PORT=30699; UID=sbs17704; PWD=JI71wtIxaPijXEIc; SECURITY=SSL; SSLServerCertificate=DigiCertGlobalRootCA.crt;", "", "")
@app.route("/")
@app.route("/index")
def home():
    return render_template("index.html")
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # get form data
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        sql = "SELECT COUNT(*) FROM users WHERE email = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, email)
        ibm_db.execute(stmt)
        result = ibm_db.fetch_assoc(stmt)

        if result['1'] > 0:
            # display error message
            return 'Email address already exists.'
        
        sql = "INSERT INTO users (name, password, email) VALUES (?, ?, ?)"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, username)
        ibm_db.bind_param(stmt, 2, password)
        ibm_db.bind_param(stmt, 3, email)
        ibm_db.execute(stmt)
        ibm_db.commit(conn)
        
        # redirect to login page
        return render_template('login.html')
    
    # display registration form
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # get form data
        email = request.form['email']
        password = request.form['password']
        
        sql = "SELECT * FROM users WHERE email = ? AND password = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, email)
        ibm_db.bind_param(stmt, 2, password)
        ibm_db.execute(stmt)
        result = ibm_db.fetch_assoc(stmt)
        
        if result:
            # store user session data
            session['logged_in'] = True
            # redirect to home page
            return render_template('upload.html')
        else:
            # display error message
            return 'Invalid login credentials.'
    # display login form
    return render_template('login.html')
@app.route("/contact" ,methods=['POST','GET'])
def contact():
    if request.method == 'POST':
        # get form data
        username = request.form['username']
        msg = request.form['msg']
        email = request.form['email']        
        sql = "INSERT INTO contact (name, msg, email) VALUES (?, ?, ?)"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, username)
        ibm_db.bind_param(stmt, 2, msg)
        ibm_db.bind_param(stmt, 3, email)
        ibm_db.execute(stmt)
        ibm_db.commit(conn)
        return render_template('index.html')    
    return render_template("contact.html")
@app.route("/about")
def about():
    return render_template("about.html")
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'logged_in' in session:
        if request.method == 'POST':
            file=request.files['image']       
            if file.filename != "Null":
                fname=file.filename
                fname=fname.replace(" ","")
                file_stream = io.BytesIO(file.read())
                cos_endpoint = "https://s3.au-syd.cloud-object-storage.appdomain.cloud"
                cos_apikey = "SKHquuq82AAbPsK14L_7mx495BofMA-hw9dFqs6LUcNr"
                cos_crn= "crn:v1:bluemix:public:cloud-object-storage:global:a/78877c7ff2e243ee8c1743dedb117b48:6e87a58a-df6e-422d-b04e-fb6209a53a4b::"
                cos = ibm_boto3.client("s3", ibm_api_key_id = cos_apikey, ibm_service_instance_id = cos_crn, endpoint_url= cos_endpoint, config= Config(signature_version = "oauth"))
                cos.put_object(Bucket = "pixelperfection" ,Key = fname ,Body=file_stream)
                inurl="https://pixelperfection.s3.au-syd.cloud-object-storage.appdomain.cloud/" + fname
                session['input']=inurl
                return render_template('option.html')
            else:
                return render_template("upload.html")
        else:
            return render_template("upload.html")
    else:
        return render_template("login.html")

@app.route('/option', methods=['GET', 'POST'])
def option():
    image=session.get('input')
    if request.method == 'POST':
        option = request.form['option']
        if option=="1":
            url = "https://human-background-removal.p.rapidapi.com/cutout/portrait/body"
            image_url = image
            response = requests.get(image_url)
            files = {'image': ('image.jpg', response.content, 'image/jpeg')}
            headers = {
                 "X-RapidAPI-Key": "18a9a4600cmsh305c1cbbadf0343p1981c9jsnc03bb8cd684f",
                 "X-RapidAPI-Host": "human-background-removal.p.rapidapi.com"
                 }
            response = requests.post(url, files=files, headers=headers)
            data = response.json()['data']
            session['output']= data['image_url']
            return redirect(url_for('download'))
        if option == "2":
            url = "https://vehicle-background-removal.p.rapidapi.com/cutout/universal/vehicle"
            image_url = image
            response = requests.get(image_url)
            files = {'image': ('image.jpg', response.content, 'image/jpeg')}
            headers = {
                "X-RapidAPI-Key": "18a9a4600cmsh305c1cbbadf0343p1981c9jsnc03bb8cd684f",
                "X-RapidAPI-Host": "vehicle-background-removal.p.rapidapi.com"
                }
            response = requests.post(url, files=files, headers=headers)
            data = response.json()['data']
            session['output']= data['elements'][0]['image_url']
            return redirect(url_for('download'))
        if option == "3":
            image_url=image
            url = "https://cartoon-yourself.p.rapidapi.com/facebody/api/portrait-animation/portrait-animation"
            response = requests.get(image_url)
            files = {'image': ('image.jpg', response.content, 'image/jpeg')}
            payload = {"type": "pixar"}
            headers = {
                      "X-RapidAPI-Key": "18a9a4600cmsh305c1cbbadf0343p1981c9jsnc03bb8cd684f",
                      "X-RapidAPI-Host": "cartoon-yourself.p.rapidapi.com"
                      }
            response = requests.post(url, data=payload, files=files, headers=headers)
            data = response.json()['data']
            session['output'] = data['image_url']
            return redirect(url_for('download'))
        if option== '4':
            url = "https://ai-skin-beauty.p.rapidapi.com/face/editing/retouch-skin"
            image_url = image
            response = requests.get(image_url)
            files = {'image': ('image.jpg', response.content, 'image/jpeg')}
            payload = {
                "retouch_degree": "1.5",
                "whitening_degree": "1.5"
                }
            headers = {
                "X-RapidAPI-Key": "18a9a4600cmsh305c1cbbadf0343p1981c9jsnc03bb8cd684f",
                "X-RapidAPI-Host": "ai-skin-beauty.p.rapidapi.com"
                }
            response = requests.post(url, data=payload, files=files, headers=headers)
            data = response.json()['data']
            print(data)
            session['output'] = data['image_url']
            return redirect(url_for('download'))
    else:
        return render_template("option.html")
@app.route('/download')
def download():
    output = session.get('output')
    return render_template('download.html',output=output)
if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0")
