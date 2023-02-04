from transformers import pipeline

classifier = pipeline("sentiment-analysis", model="michellejieli/emotion_text_classifier")

def get_emotion(text):
    return classifier(text)[0]["label"]
