from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def compute_match_score(job_text, resume_text):
    """Return a match percentage between 0 and 100."""
    vectorizer = TfidfVectorizer().fit_transform([job_text, resume_text])
    vectors = vectorizer.toarray()
    sim = cosine_similarity(vectors)[0,1]
    return round(sim * 100, 2)

def rank_resumes(job_text, resumes_text_list):
    """Return list of (index, score) sorted by score descending."""
    all_texts = [job_text] + resumes_text_list
    vectorizer = TfidfVectorizer().fit_transform(all_texts)
    vectors = vectorizer.toarray()
    job_vector = vectors[0].reshape(1, -1)
    resume_vectors = vectors[1:]
    scores = cosine_similarity(job_vector, resume_vectors).flatten()
    ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
    return [(idx, round(score*100,2)) for idx, score in ranked]