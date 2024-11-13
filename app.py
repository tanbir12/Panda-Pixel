
# This Code is Published by Tanbir Pradhan. Don't use it in your project.

import os
from flask import Flask , render_template , request , redirect ,url_for
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

# _________________________________________________________________Youtube Data Api__________________________________________________________________
# Import Module
from googleapiclient.discovery import build


#+++++++++++++++++++++++++++ CONFIGURE ++++++++++++++++++++++++++++++++++++++++++
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pandapixels.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True



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
# with app.app_context():
#         db.create_all()


#___________________Api key________________________
api_key = 'AIzaSyBNUon-AZsjSKXpTzcCN7ZS3up9RyuVi4A'


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

        if(username == "ommpratyush" and password == "6371704944"):
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


if __name__=="__main__":
    app.run(debug=True, port=8000)


