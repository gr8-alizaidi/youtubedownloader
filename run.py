from flask import Flask,request,jsonify,send_file,make_response
from flask_cors import CORS
from flask.templating import render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import json
from pytube import YouTube
from pytube import Playlist
import zipfile
from werkzeug.exceptions import RequestURITooLarge
from werkzeug.wrappers import Response
import youtube_dl,os
import pafy


app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
api_key="AIzaSyCKr4GluXO438EY__-UMHdC2Qd_3j1cVYw"

class channelsearch(FlaskForm):
    channelid=StringField("Channel ID",validators=[DataRequired()])
    submit=SubmitField("Search")

class playlistsearch(FlaskForm):
    playlistid=StringField("Playlist ID",validators=[DataRequired()])
    submit=SubmitField("Search")

class videosearch(FlaskForm):
    videoid=StringField("Video ID",validators=[DataRequired()])
    submit=SubmitField("Search")


@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def home():
    return render_template("home.html")

@app.route("/channel", methods=['GET', 'POST'])
def channel():
    form=channelsearch()
    if form.validate_on_submit():
        
        a=apicallchannel(form.channelid.data)
        return render_template("channel.html",form=form,id=form.channelid.data,a=a)       
    return render_template("channel.html",form=form)

@app.route("/playlist", methods=['GET', 'POST'])
def playlist():
    form=playlistsearch()
    if form.validate_on_submit():
        a=apiplaylist(form.playlistid.data)
        return render_template("playlist.html",form=form,id=form.playlistid.data,a=a)   
    return render_template("playlist.html",form=form)


@app.route("/video", methods=['GET', 'POST'])
def video():
    form=videosearch()
    if form.validate_on_submit():
         url='http://youtube.com/watch?v='+form.videoid.data
         try:
            vid=form.videoid.data
            my_video = YouTube(url)
            fname=(my_video.title)
            pic=my_video.thumbnail_url
            return render_template("video.html",form=form,fname=fname,pic=pic,a="done",vid=vid)
         except:
                 return render_template("video.html",form=form,a="error")
    return render_template("video.html",form=form)

# @app.route("/daudio/<string:vid>")
# def daudio(vid):
#     url='http://youtube.com/watch?v='+vid
#     my_video = YouTube(url)
#     fname=(my_video.title)
#     stream = my_video.streams.get_by_itag(251)
    
#     return send_file(stream.download(),as_attachment=True)
@app.route("/daudio/<string:vid>")
def daudio(vid):
    url='http://youtube.com/watch?v='+vid
    yt = YouTube(url)
    video = yt.streams.filter(only_audio=True).first()
    out_file = video.download()
  
    # save the file
    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'
    os.rename(out_file, new_file)
    
    return send_file(new_file,as_attachment=True)

@app.route("/dvideohq/<string:vid>")
def dvideohq(vid):
    url='http://youtube.com/watch?v='+vid
    my_video = YouTube(url)
    fname=(my_video.title)
    return send_file(my_video.streams.filter(progressive=True).order_by('resolution').desc()[0].download(),as_attachment=True)

@app.route("/dvideolq/<string:vid>")
def dvideolq(vid):
    url='http://youtube.com/watch?v='+vid
    my_video = YouTube(url)
    fname=(my_video.title)
    return send_file(my_video.streams.filter(progressive=True).order_by('resolution')[0].download(),as_attachment=True)

@app.route("/dpvall/<string:pid>")
def dpvall(pid):
    url="https://www.youtube.com/playlist?list="+pid
    try:
        playlist = Playlist(url)
        zipf = zipfile.ZipFile('gettube.zip','w', zipfile.ZIP_DEFLATED)
        for video in playlist:   
            my_video = YouTube(video)
            zipf.write(my_video.streams.filter(progressive=True).order_by('resolution')[0].download())
        zipf.close()
        return send_file('gettube.zip',
            mimetype = 'zip',
            attachment_filename= 'gettube.zip',
            as_attachment = True)
                    
    except:
        return "error"


@app.route("/dcvall/<string:cid>")
def dcvall(cid):
    try:
        a=apicallchannel(cid)
        zipf = zipfile.ZipFile('gettube.zip','w', zipfile.ZIP_DEFLATED)
        for i in a["items"]:
            url="http://youtube.com/watch?v="+i["id"]["videoId"]
            my_video = YouTube(url)
            zipf.write(my_video.streams.filter(progressive=True).order_by('resolution')[0].download())
        zipf.close()
    finally:
        return send_file('gettube.zip',
                    mimetype = 'zip',
                    attachment_filename= 'gettube.zip',
                    as_attachment = True)
                            
        

@app.route("/dcaall/<string:cid>")
def dcaall(cid):
    try:
        a=apicallchannel(cid)
        zipf = zipfile.ZipFile('gettube.zip','w', zipfile.ZIP_DEFLATED)
        for i in a.items():
            url="http://youtube.com/watch?v="+i["id"]["videoId"]
            yt = YouTube(url)
            video = yt.streams.filter(only_audio=True).first()
            out_file = video.download()
        
            # save the file
            base, ext = os.path.splitext(out_file)
            new_file = base + '.mp3'
            os.rename(out_file, new_file)
            zipf.write(new_file)
            
            remove_file(new_file)
        zipf.close()
    finally:
        return send_file('gettube.zip',
                    mimetype = 'zip',
                    attachment_filename= 'gettube.zip',
                    as_attachment = True)
                            
    
    
@app.route("/dpaall/<string:pid>")
def dpaall(pid):
    url="https://www.youtube.com/playlist?list="+pid
    try:
        playlist = Playlist(url)
        zipf = zipfile.ZipFile('gettube.zip','w', zipfile.ZIP_DEFLATED)
        for video in playlist:   
            yt = YouTube(video)
            video = yt.streams.filter(only_audio=True).first()
            out_file = video.download()
            # save the file
            base, ext = os.path.splitext(out_file)
            new_file = base + '.mp3'
            os.rename(out_file, new_file)
            zipf.write(new_file)
            remove_file(new_file)
        zipf.close()
        return send_file('gettube.zip',
            mimetype = 'zip',
            attachment_filename= 'gettube.zip',
            as_attachment = True)                   
    except:
        return "error"

def remove_file(nf):
                try:
                    os.remove(nf)
                except Exception as error:
                    app.logger.error("Error removing or closing downloaded file handle", error)
def get_mp3(url):
  
  #gets video information from url
    video_info = youtube_dl.YoutubeDL().extract_info(
        url, download=False
    )
    video = pafy.new(url)
    file_name = video.title+".mp3"
    options = {
        'format': 'bestaudio/best',
        'keepvideo': False,
        'outtmpl': file_name,
        # conversion
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }
    
    #downloads song with above parameters
    with youtube_dl.YoutubeDL(options) as download:
        download.download([url])

    return file_name

    
            
def apivideo(a):
    url="https://youtube.googleapis.com/youtube/v3/videos?part=snippet%2CcontentDetails%2Cstatistics&id="+a+"&key="+api_key
    response=requests.get(url)
    if response.status_code==200:
        return json.loads(response.text)
    else:
        return "error"
def apiplaylist(a):
   
    url="https://youtube.googleapis.com/youtube/v3/playlistItems?part=snippet%2CcontentDetails&maxResults=25&playlistId="+a+"&maxResults=5&key="+api_key
    response=requests.get(url)
    if response.status_code==200:
        return json.loads(response.text)
    else:
        return "error"


def apicallchannel(a):
    url="https://www.googleapis.com/youtube/v3/search?order=date&part=snippet&channelId="+a+"&maxResults=5&key="+api_key
    response=requests.get(url)
    if response.status_code==200:
        return json.loads(response.text)
    else:
        return "error"

def apicalluser(a):
    url="https://youtube.googleapis.com/youtube/v3/channels?part=snippet%2CcontentDetails%2Cstatistics&forUsername=SyedNadeemSarwar&key="+api_key   

if __name__ == "__main__":
    app.run(debug=True)