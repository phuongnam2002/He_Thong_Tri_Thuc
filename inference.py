from database import diseases
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def preprocess(symptoms):
    sym_text = ''
    for symptom in symptoms:
        sym_text = sym_text + ' ' + symptom.replace(' ', '_')
    return sym_text


train_data = []
for disease in diseases:
    advance_symptoms = disease['advance_symptoms']
    base_symptoms = disease['base_symptoms']
    train_data.append(preprocess(advance_symptoms))

vectorizer = TfidfVectorizer(min_df=0)
vectorizer.fit(train_data)


def get_vector(symptoms):
    ft = preprocess(symptoms)
    vec = vectorizer.transform([ft])
    return vec


def infer_tfidf(symptoms):
    macthed = []
    for disease in diseases:

        disease_symtom = disease['base_symptoms'] + disease['advance_symptoms']
        user_symptom = list(set(symptoms) & set(disease_symtom))

        user_symptom_vec = get_vector(user_symptom)
        disease_vec = get_vector(disease_symtom)

        score = cosine_similarity(user_symptom_vec, disease_vec)[0][0]

        if score > 0:
            macthed.append((disease['name'], score))
    return macthed
