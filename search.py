import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import pathlib
from bs4 import BeautifulSoup
import logging
import shutil

def inject_ga():
    GA_ID = "google_analytics"
    GA_JS = """
    <!-- Google tag (gtag.js) -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-N39RFTGS8Q"></script>

        <script>
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());

            gtag('config', 'G-N39RFTGS8Q');
        </script>
    """

    # Insert the script in the head tag of the static template inside your virtual
    index_path = pathlib.Path(st.__file__).parent / "static" / "index.html"
    logging.info(f'editing {index_path}')
    soup = BeautifulSoup(index_path.read_text(), features="html.parser")
    if not soup.find(id=GA_ID): 
        bck_index = index_path.with_suffix('.bck')
        if bck_index.exists():
            shutil.copy(bck_index, index_path)  
        else:
            shutil.copy(index_path, bck_index)  
        html = str(soup)
        new_html = html.replace('<head>', '<head>\n' + GA_JS)
        index_path.write_text(new_html)


inject_ga()

class AyatSearch():

    def __init__(self, path):

        df = pd.read_csv('data/main_df.csv')
        arabic = []
        self.text=[]
        for index, row in df.iterrows():
            arabic.append(row['Arabic'])
            t = ""
            t += row['Name'] + "|" + str(row['Arabic'])+"|"+ str(row['Surah'])+"|"+str(row['Ayat'])+"|"
            t += row['EnglishTitle'] + "|" + str(row['ArabicTitle'])+"|"+ str(row['RomanTitle'])+"|"
            t += row['PlaceOfRevelation'] + "|"
            for j in range(1, 4):
                t += row['Translation' + str(j)] + ";"
            t += "|"
            for j in range(1, 3):
                t+= row['Tafaseer' + str(j)] + ";"
            t = t[:-1]
            self.text.append(t)
        
        self.vectorizer = TfidfVectorizer()
        self.X = self.vectorizer.fit_transform(self.text)
        
        
    def query(self, query, top_k=5):
        query_vec = self.vectorizer.transform([query])
        sim_scores = cosine_similarity(query_vec, self.X).flatten()
        top_indices = sim_scores.argsort()[::-1][:top_k]
        top_paragraphs = [self.text[i] for i in top_indices]
        return top_paragraphs



st.title("Welcome to Islam & AI")
st.write("Your personal AI assistant that uses Quranic Ayats to search for your queries! Our model is based on Natural Language Processing techniques and is designed to help you find relevant information from the Quran quickly and easily. Whether you have a question about Islamic beliefs, practices, or anything else related to Islam, just ask our AI assistant and it will provide you with the most relevant Quranic Ayats to answer your query.")
st.write("This is the initial model for a very big project, please give feedback, share & let us know about any questions you might have")

search = AyatSearch("data/main_df.csv")

st.subheader("Enter your query:")
query = st.text_input("", "Importance of Prayer")#st.session_state.query)
# st.session_state.query = query
st.subheader("Select the number of queries:")
x = st.slider("", 2, 25, 3)
# from translate import Translator


# print 

# translator = Translator(to_lang=option.lower())
# translation = translator.translate(query  )
results = search.query(query, int(x))

st.title("**Results:**")

for r in results:
    # Questions
    text = r.split("|")
    st.subheader(f"{text[1]}")
    st.write(f"**- Surah Name: {text[5]} | {text[4]} | {text[6]} | {text[0]}**")
    st.write(f"**- Surah No. {text[2]} | Ayat No. {text[3]}**")
    st.write(f"**- Surah Revealed in {text[7]}**")

    # Answers
    st.subheader("Translations:")
    translations = text[-2].split(";")
    for i in range(len(translations)):
        if len(translations[i])>2:
            st.write(f"{i+1}: {translations[i]}")

    st.subheader("Tafaseer:")
    tafaseer = text[-1].split(";")
    for i in range(len(tafaseer)):
        if len(tafaseer[i])>2:
            st.write(f"{i+1}: {tafaseer[i]}")
        
    st.subheader("-"*70)
# st.write(f"{results}")





