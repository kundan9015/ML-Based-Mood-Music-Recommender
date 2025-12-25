from flask import Flask, render_template, request, url_for, send_from_directory, send_file
import joblib
import random
import os
import logging
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='static', static_url_path='/static')

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load the trained model and label encoder
model = joblib.load("mood_model.pkl")
le = joblib.load("label_encoder.pkl")

# Song database (unchanged, assuming filenames are correct)
song_db = {
    'Happy': [
        {'name': 'Yaarian (ABCD)', 'artist': 'Yo Yo Honey Singh', 'img': 'happy1.jpg', 'file': 'happy1.mp3'},
        {'name': 'Tere Te', 'artist': 'Guru Randhawa', 'img': 'happy2.jpg', 'file': 'happy2.mp3'},
        {'name': 'Jatt Diyan Tauran', 'artist': 'Gippy Grewal, Shipra Goyal', 'img': 'happy3.jpg', 'file': 'happy3.mp3'},
        {'name': 'Jeene Ke Hain Char Din', 'artist': 'Sonu Nigam, Sunidhi Chauhan', 'img': 'happy4.jpg', 'file': 'happy4.mp3'},
        {'name': 'Supreme', 'artist': 'Shubh', 'img': 'happy5.jpg', 'file': 'happy5.mp3'},
        {'name': 'Be Mine', 'artist': 'Shubh', 'img': 'happy6.jpg', 'file': 'happy6.mp3'}
    ],
    'Sad': [
        {'name': 'Kabhi Sham Dhale', 'artist': 'Mohammad Faiz', 'img': 'sad1.jpg', 'file': 'sad1.mp3'},
        {'name': 'Nira Ishq', 'artist': 'Guri', 'img': 'sad2.jpg', 'file': 'sad2.mp3'},
        {'name': 'Pal Pal Dil Ke Paas', 'artist': 'Arijit Singh', 'img': 'sad3.jpg', 'file': 'sad3.mp3'},
        {'name': 'Pal', 'artist': 'Arijit Singh, Javed Mohsin', 'img': 'sad4.jpg', 'file': 'sad4.mp3'},
        {'name': 'Tum Hi Ho', 'artist': 'Mithoon, Arijit Singh', 'img': 'sad5.jpg', 'file': 'sad5.mp3'},
        {'name': 'Tera Hone Laga Hoon', 'artist': 'Atif Aslam, Alisha Chinai', 'img': 'sad6.jpg', 'file': 'sad6.mp3'}
    ],
    'Motivational': [
        {'name': '52 Bars', 'artist': 'Karan Aujla', 'img': 'mot1.jpg', 'file': 'mot1.mp3'},
        {'name': 'Father Saab', 'artist': 'Khasa Aala Chahar', 'img': 'mot2.jpg', 'file': 'mot2.mp3'},
        {'name': 'Game', 'artist': 'Shooter Kahlon, Sidhu Moosewala', 'img': 'mot3.jpg', 'file': 'mot3.mp3'},
        {'name': 'Get Ready To Fight', 'artist': 'Benny Dayal', 'img': 'mot4.jpg', 'file': 'mot4.mp3'},
        {'name': 'Winning Speech', 'artist': 'Karan Aujla', 'img': 'mot5.jpg', 'file': 'mot5.mp3'},
        {'name': 'Aarambh Hai Prachand', 'artist': 'K.K Menon, Abhimannyu Singh', 'img': 'mot6.jpg', 'file': 'mot6.mp3'}
    ],
    'Party': [
        {'name': 'Abhi Toh Party Shuru Hui Hai', 'artist': 'Badshah, Aastha Gill', 'img': 'party1.jpg', 'file': 'party1.mp3'},
        {'name': '5 Taara', 'artist': 'Diljit Dosanjh, Jatinder Shah', 'img': 'party2.jpg', 'file': 'party2.mp3'},
        {'name': 'Daaru Party', 'artist': 'Millind Gaba', 'img': 'party3.jpg', 'file': 'party3.mp3'},
        {'name': 'Party All Night', 'artist': 'Yo Yo Honey Singh', 'img': 'party4.jpg', 'file': 'party4.mp3'},
        {'name': 'Kala Chashma', 'artist': 'Prem Hardeep, Badshah, Neha Kakkar', 'img': 'party5.jpg', 'file': 'party5.mp3'},
        {'name': 'Tujhe Aksa Beach Ghuma Doon', 'artist': 'Wajid, Amrita Kak', 'img': 'party6.jpg', 'file': 'party6.mp3'}
    ]
}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            energy = float(request.form['energy'])
            dance = float(request.form['danceability'])
            valence = float(request.form['valence'])

            if not (1 <= energy <= 10 and 1 <= dance <= 10 and 1 <= valence <= 10):
                return render_template("index.html", mood=None, error="Please enter values between 1 and 10")

            prediction = model.predict([[energy, dance, valence]])[0]
            mood = le.inverse_transform([prediction])[0]

            songs = random.sample(song_db[mood], min(6, len(song_db[mood])))

            for song in songs:
                # Use lowercase 'image' folder
                image_path = os.path.join('static', 'image', song['img'])
                if not os.path.exists(image_path):
                    logger.error(f"Image not found: {image_path}")
                    song['image_url'] = url_for('static', filename='placeholder.jpg', _external=True)
                else:
                    song['image_url'] = url_for('static', filename=f'image/{song["img"]}', _external=True)
                # Use lowercase 'audio' folder
                song['audio_url'] = url_for('serve_audio', filename=song["file"], _external=True)
                logger.debug(f"Song: {song['name']}, Image URL: {song['image_url']}, Audio URL: {song['audio_url']}")

            return render_template("index.html", mood=mood, songs=songs)
        except ValueError:
            return render_template("index.html", mood=None, error="Please enter valid numbers")
        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")
            return render_template("index.html", mood=None, error=f"An error occurred: {str(e)}")

    return render_template("index.html", mood=None)

@app.route('/static/<path:filename>')
def serve_static(filename):
    try:
        logger.debug(f"Serving static file: {filename}")
        return send_from_directory('static', filename)
    except Exception as e:
        logger.error(f"Error serving static file {filename}: {str(e)}")
        return str(e), 404

@app.route('/audio/<path:filename>')
def serve_audio(filename):
    try:
        logger.debug(f"Attempting to serve audio file: {filename}")
        audio_path = os.path.join('static', 'audio', filename)  # Changed 'Audio' to 'audio'
        logger.debug(f"Full audio path: {audio_path}")

        if not os.path.exists(audio_path):
            logger.error(f"Audio file not found: {audio_path}")
            return "Audio file not found", 404

        return send_file(
            audio_path,
            mimetype='audio/mpeg',
            as_attachment=False
        )
    except Exception as e:
        logger.error(f"Error serving audio file {filename}: {str(e)}")
        return str(e), 500

if __name__ == "__main__":
    app.run(debug=True)