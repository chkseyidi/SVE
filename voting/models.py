from django.db import models
from account.models import CustomUser
from django.utils.translation import gettext_lazy as _
from nltk.sentiment import SentimentIntensityAnalyzer
from googletrans import Translator
# Create your models here.
class Voter(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    phone = models.CharField(max_length=11, unique=True)  # Used for OTP
    otp = models.CharField(max_length=10, null=True)
    verified = models.BooleanField(default=False)
    voted = models.BooleanField(default=False)
    otp_sent = models.IntegerField(default=0)  # Control how many OTPs are sent

    def __str__(self):
        return self.admin.last_name + ", " + self.admin.first_name


class Position(models.Model):
    name = models.CharField(max_length=50, unique=True)
    max_vote = models.IntegerField()
    priority = models.IntegerField()

    def __str__(self):
        return self.name




class Candidate(models.Model):
    fullname = models.CharField(max_length=50)
    photo = models.ImageField(upload_to="candidates")
    bio = models.TextField()
    position = models.ForeignKey(Position, on_delete=models.CASCADE)

    sentiment_score = models.FloatField(null=True, blank=True)
    sentiment_category = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.fullname

    def save(self, *args, **kwargs):
        # Effectuez l'analyse de sentiment lors de la sauvegarde du candidat
        score, category = self.analyse_sentiment()
        self.sentiment_score = score['compound']
        self.sentiment_category = category
        super().save(*args, **kwargs)

    def analyse_sentiment(self):
        # Traduction du texte
        translator = Translator()
        bio_en = translator.translate(self.bio, src='fr', dest='en').text

        # Analyse du sentiment
        sia = SentimentIntensityAnalyzer()
        score = sia.polarity_scores(bio_en)

        # Classification du sentiment
        seuil_positif = 0.5
        seuil_neutre_inf = -0.5
        seuil_neutre_sup = 0.5

        if score['compound'] >= seuil_positif:
            categorie_sentiment = 'positif'
        elif seuil_neutre_inf <= score['compound'] < seuil_neutre_sup:
            categorie_sentiment = 'neutre'
        else:
            categorie_sentiment = 'négatif'

        return score, categorie_sentiment



class Votes(models.Model):
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
