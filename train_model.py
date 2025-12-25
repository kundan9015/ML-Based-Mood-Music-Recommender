import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib


df = pd.read_csv("mood_song_dataset.csv")

X = df[['Energy','Danceability','Valence']]
y = df['Mood']

le = LabelEncoder()

y_encoded = le.fit_transform(y)

X_train, X_test,y_train,y_test = train_test_split(X,y_encoded,test_size=0.2,random_state=42)
model = RandomForestClassifier(n_estimators=100,random_state=42)
model.fit(X_train,y_train)

joblib.dump(model,'mood_model.pkl')
joblib.dump(le,'label_encoder.pkl')

accuracy = model.score(X_test,y_test)
print(f"Model trained with with accuracy : {accuracy:.2f}")
