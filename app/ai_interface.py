import pickle

def load_ai_model(model_path='ai/password_model.pkl', vectorizer_path='ai/vectorizer.pkl'):
    with open(model_path, 'rb') as model_file:
        model = pickle.load(model_file)
    with open(vectorizer_path, 'rb') as vec_file:
        vectorizer = pickle.load(vec_file)
    return model, vectorizer

def predict_password_strength(password, model, vectorizer):
    X = vectorizer.transform([password])
    return model.predict(X)[0]
