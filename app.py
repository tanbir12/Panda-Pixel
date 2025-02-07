
# This Code is Published by Tanbir Pradhan. Don't use it in your project.

import os
from flask import Flask , render_template , request , redirect ,url_for
from flask_sqlalchemy import SQLAlchemy
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
app = Flask(__name__)

# _________________________________________________________________Youtube Data Api__________________________________________________________________
# Import Module
from googleapiclient.discovery import build


#+++++++++++++++++++++++++++ CONFIGURE ++++++++++++++++++++++++++++++++++++++++++
app.config ['SQLALCHEMY_DATABASE_URI'] = os.getenv('Database_Uri')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# import .env file
from dotenv import load_dotenv
load_dotenv()
Username = os.getenv('Admin')
Password = os.getenv('Password')
api_key = os.getenv('API_KEY')

sender_email = os.getenv('senderEmail')
sender_password = os.getenv('senderSecret')
recipient_email = os.getenv('adminEmail')
        
#++++++++++++++++++++++++++++ DATABASE AREA ++++++++++++++++++++++++++++++++++++++
db = SQLAlchemy(app)

class filedbs(db.Model):
   id = db.Column('file_id', db.Integer, primary_key = True)
   file_name = db.Column(db.String(40))
   file_img = db.Column(db.String(30))
   file_link = db.Column(db.String(200))
   
   
   def __init__(self,file_name,file_img,file_link):
       self.file_name = file_name
       self.file_img = file_img
       self.file_link = file_link    


# ++++++++++++++++++++++++++++++    For Creating The Database db  ++++++++++++++++++++++++++++++++++
with app.app_context():
        db.create_all()



# Create YouTube Object
youtube = build('youtube', 'v3',
				developerKey=api_key)

ch_request = youtube.channels().list(
	part='statistics',
	id='UCCrYjmEDVNggjBjrStpUypQ').execute()


# ++++++++++++++++++++++++++ Youtube Data Variables +++++++++++++++++++++++++++

no_of_subscriber = ch_request['items'][0]['statistics']['subscriberCount']
no_of_videos = ch_request['items'][0]['statistics']['videoCount']
no_of_views = ch_request['items'][0]['statistics']['viewCount']




#++++++++++++++++++++++++++++  Home Page Route  ++++++++++++++++++++++++++++++++
@app.route("/")
def hello_world():

    playlist = youtube.playlistItems().list(
    part = 'snippet,contentDetails',
    playlistId = 'PLogt1cqCw0BW0Rk09hJrsxgQPsy8WtR9R',
    maxResults = 9).execute()
    items = []
    for i in range(9):
        item = []
        #For getting Thumbnail from the playlist json file it return a url
        thumbnail = playlist['items'][i]['snippet']['thumbnails']['medium']['url']
        item.append(thumbnail)

        #For getting Title from the playlist json file it return a string
        #For getting description use description instead title
        title = playlist['items'][i]['snippet']['title']
        item.append(title)

        #For getting VideoId and Published date
        video_id = playlist['items'][i]['contentDetails']['videoId']
        item.append(video_id)
        video_date = playlist['items'][i]['contentDetails']['videoPublishedAt']
        item.append(video_date)
        items.append(item)

    filedb = filedbs.query.all()
    filedb = list(filedb)
    filedb = filedb[:2]
    filedb = filedb[::-1]


    return render_template("index.html",items = items,dbs = filedb ,nosub = no_of_subscriber,novid = no_of_videos,noview = no_of_views)




# +++++++++++++++++++++++++++  Videos Route  ++++++++++++++++++++++++++++++++++++
@app.route("/Videos")
def show_video():

    playlist = youtube.playlistItems().list(
    part = 'snippet,contentDetails',
    playlistId = 'PLogt1cqCw0BW0Rk09hJrsxgQPsy8WtR9R',
    maxResults = 39).execute()
    items = []
    for i in range(39):
        item = []
        #For getting Thumbnail from the playlist json file it return a url
        thumbnail = playlist['items'][i]['snippet']['thumbnails']['medium']['url']
        item.append(thumbnail)

        #For getting Title from the playlist json file it return a string
        #For getting description use description instead title
        title = playlist['items'][i]['snippet']['title']
        item.append(title)

        #For getting VideoId and Published date
        video_id = playlist['items'][i]['contentDetails']['videoId']
        item.append(video_id)
        video_date = playlist['items'][i]['contentDetails']['videoPublishedAt']
        item.append(video_date)
        items.append(item)
        
        

    return render_template("video.html",items=items,nosub = no_of_subscriber,novid = no_of_videos,noview = no_of_views)


#++++++++++++++++++++++++++++++  Models Route  +++++++++++++++++++++++++++++++++++

@app.route("/Models")
def Show_Models():

    filedb = filedbs.query.all()
    filedb = list(filedb)
    filedb = filedb[::-1]
    return render_template("model.html", dbs = filedb , nosub = no_of_subscriber, novid = no_of_videos, noview = no_of_views)




#+++++++++++++++++++++++++++++  Admin  Route  +++++++++++++++++++++++++++++++++++++

@app.route("/Admin",methods = ['GET','POST'])
def Admin_Auth():

    if request.method== "POST":
        username = request.form.get("userName")
        password = request.form.get("password")

        if(username == Username and password == Password):
            return redirect(url_for('GET_Value'))
        else :
            return render_template("index.html")

    return render_template("admin.html")


@app.route("/Upload",methods = ['GET','POST'])
def GET_Value():

    if request.method == 'POST':
        fileName = request.form.get("model_name")
        fileLink = request.form.get("model_url")
        fileImg =  request.files['model_img']

        if (str(fileName)!="" and str(fileLink)!=""):
            filedb = filedbs(fileName,fileImg.filename,fileLink)
            db.session.add(filedb)
            db.session.commit()

            # when saving the file
            fileImg.save(os.path.join(app.static_folder, 'Model_Images', fileImg.filename))
            
            return "Uploaded Successfully...."

    return render_template('upload.html')



# +++++++++++++++++++++++++++++++++++++++  DELETE ROUTE  ++++++++++++++++++++++++++++++++++++++++++++++++++

@app.route("/Delete" , methods = ['GET','POST'])
def Delete_model():
    if request.method == 'POST':
        fileID = request.form.get("model_id")

        if(str(fileID) !=""):
            data = filedbs.query.filter_by( id = fileID).first()
        
            try:
                os.remove(app.static_folder+'/Model_Images/'+str(data.file_img))
            except:
                pass
            
            filedbs.query.filter_by( id = fileID).delete()
            db.session.commit()
            return  "+++  DELETE SUCCESSFULL  +++"



    return render_template('delete.html')


# +++++++++++++++++++++++++++++++++++++++  Mail Sending Route  ++++++++++++++++++++++++++++++++++++++++++++++++++
@app.route('/sendEmail',methods = ['GET','POST'])
def Send_Email():
    if request.method == "POST":
        Name = request.form.get('senderName')
        Email = request.form.get('senderEmail')
        Text = request.form.get('senderText')

        subject = "Panda Pixels Website Mail"
        body = "<<--!!  This Mail is Autometically Generated from Panda Pixels Website.  !!-->>\n\n"+ f"From : {Email} \nSender Name : {Name} \n\n" +Text

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            text = msg.as_string()
            server.sendmail(sender_email, recipient_email, text)
            server.quit()
            return render_template('successful.html')
        except Exception as e:
            return f"Error: {e}"






if __name__=="__main__":
    app.run(debug=True, port=8000)


