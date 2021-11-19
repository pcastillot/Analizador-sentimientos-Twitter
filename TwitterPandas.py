import pandas as pd
import re
import unicodedata
import string
from PyQt5.QtCore import QAbstractTableModel, Qt
from main_ui import *
from textblob import TextBlob
import tweepy
from PyQt5 import QtWidgets

consumer_key = "cFXQjyvc7dz29o4FVuqLpwCPH"
consumer_secret = "bGIT8c2o56BCMelNiUTXwwA9jsJJZ0w4lJx5fRkJQF8Y38wtJv"
access_token = "598430996-6QUpYRwPsbk9RSysGFnvEUwvXyzOVub72Swu8SXT"
access_secret = "kJRhwoCk3XC1Tv5w9GiKU03m1fLKsHwRrdKjSMxeSvOxx"


#Clase para crear un modelo pandas y pasarlo a la TableView
class PandasModel(QAbstractTableModel):

	def __init__(self, data):
		QAbstractTableModel.__init__(self)
		self._data = data

	def rowCount(self, parent=None):
		return self._data.shape[0]

	def columnCount(self, parnet=None):
		return self._data.shape[1]

	def data(self, index, role=Qt.DisplayRole):
		if index.isValid():
			if role == Qt.DisplayRole:
				return str(self._data.iloc[index.row(), index.column()])
		return None

	#Titulo de las columnas
	def headerData(self, col, orientation, role):
		if orientation == Qt.Horizontal and role == Qt.DisplayRole:
			return self._data.columns[col]
		return None


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
	def __init__(self, *args, **kwargs):
		# Inicializacion de la ventana y listeners
		QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
		self.setupUi(self)
		self.btnGetTweets.clicked.connect(lambda: self.get_tweets(self.txtUser.toPlainText(), int(self.spinTweets.text())))

	# method to get a user's last tweets
	def get_tweets(self, username, ntweets):
		# http://tweepy.readthedocs.org/en/v3.1.0/getting_started.html#api
		auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
		auth.set_access_token(access_token, access_secret)
		api = tweepy.API(auth)

		# get tweets
		tweets_for_df = []
		for tweet in tweepy.Cursor(api.user_timeline, screen_name=username).items(ntweets):
			# create array of tweet information: username, tweet id, date/time, text
			tweet_limpio = self.tokenizar(str(tweet.text.encode("utf-8")))
			polaridad, carita = self.analisisSentimiento(tweet_limpio)
			tweets_for_df.append([username, tweet.id_str, tweet.created_at, polaridad, tweet.text.encode("utf-8"), tweet_limpio])

		df = pd.DataFrame(data=tweets_for_df, columns=["Usuario", "TweetID", "Fecha", "Polaridad", "Tweet No Procesado", "Tweet Procesado"])
		self.mostrar_datos(df)

	def mostrar_datos(self, df):
		model = PandasModel(df)
		self.tv.setModel(model)
		self.tv.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
		self.tv.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
		self.tv.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
		self.tv.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
		self.tv.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
		self.tv.horizontalHeader().setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
		self.tv.show()

	def strip_accents(self, s):
		return ''.join(c for c in unicodedata.normalize('NFD', s)
					   if unicodedata.category(c) != 'Mn')

	def deEmojify(self, text):
		regrex_pattern = re.compile(pattern="["
											u"\U0001F600-\U0001F64F"  # emoticons
											u"\U0001F300-\U0001F5FF"  # symbols & pictographs
											u"\U0001F680-\U0001F6FF"  # transport & map symbols
											u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
											"]+", flags=re.UNICODE)
		return regrex_pattern.sub(r'', text)

	def tokenizar(self, mi_texto):
		# funcion alternativa de limpieza de tweets, en desuso por ahora
		# tknzr = TweetTokenizer(strip_handles=True)
		# clean_text = tknzr.tokenize(mi_texto)

		# elimina los links
		clean_text = self.strip_accents(mi_texto)
		# elimina los links
		clean_text = re.sub(r"http\S+", "", clean_text)
		# elimina los text que me caen mal
		clean_text = re.sub(r"Text", "", clean_text)
		# elimina los RT y las menciones
		clean_text = re.sub('RT @[\w_]+: ', '', clean_text)
		# elimina los saltos de linea
		clean_text = re.sub(r"\n??", '', clean_text)
		# remplaza signos de puntuacion por espacios
		clean_text = re.sub('[%s]' % re.escape(string.punctuation), " ", clean_text)
		# elimina los caracteres solitarios, como las n
		clean_text = re.sub(r'(?:^| )\w(?:$| )', ' ', clean_text).strip()

		# lo pasa a minusculas
		clean_text = clean_text.lower()

		# elimina números y palabras que contengan números
		clean_text = re.sub('\w*\d\w*', ' ', clean_text)
		# elimina emojis
		clean_text = self.deEmojify(clean_text)
		return clean_text

	def analisisSentimiento(self, texto):
		polaridad = 0
		carita = 0
		analysis = TextBlob(texto)
		#try:
		#	if analysis.detect_language() != 'en':
		#		time.sleep(0.2)
		#		analysis.translate(to='en')

		polaridad = analysis.sentiment.polarity

		if polaridad > 0:
			carita = 1
		elif polaridad < 0:
			carita = -1

		#except:
		#	print ("El elemento no está presente")
		#	jo = 0

		#time.sleep(0.2)
		return polaridad, carita



if __name__ == "__main__":
	app = QtWidgets.QApplication([])
	window = MainWindow()
	window.show()
	app.exec_()