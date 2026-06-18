from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from collections import Counter
import re
import time

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():

    if request.method == 'POST':

        url = request.form['url']

        try:

            start = time.time()

            page = requests.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0"
                },
                timeout=10
            )

            response_time = round(time.time() - start, 2)

            soup = BeautifulSoup(page.text, 'html.parser')

            # TEXT ANALYSIS
            text = soup.get_text().lower()

            words = re.findall(r'\b[a-z]{4,}\b', text)

            stop_words = {
                "this", "that", "with", "from", "have", "will",
                "your", "about", "they", "their", "what",
                "when", "where", "which", "there", "would",
                "could", "should", "into", "than", "then"
            }

            filtered_words = [
                word for word in words
                if word not in stop_words
            ]

            top_keywords = Counter(filtered_words).most_common(10)

            # TITLE
            if soup.title:
                title = soup.title.get_text(strip=True)
                title_score = 20
            else:
                title = "No Title Found"
                title_score = 0

            # META DESCRIPTION
            meta = soup.find("meta", attrs={"name": "description"})

            if meta:
                description = meta.get("content")
                meta_score = 20
            else:
                description = "No Meta Description Found"
                meta_score = 0

            # H1 TAGS
            h1_count = len(soup.find_all("h1"))

            if h1_count > 0:
                h1_score = 15
            else:
                h1_score = 0

            # IMAGE ANALYSIS
            images = soup.find_all("img")

            image_count = len(images)

            missing_alt = 0

            for img in images:
                if not img.get("alt"):
                    missing_alt += 1

            if image_count == 0:
                image_score = 15
            elif missing_alt == 0:
                image_score = 15
            else:
                image_score = max(0, 15 - missing_alt)

            # LINK ANALYSIS
            links = soup.find_all("a")

            internal_links = 0
            external_links = 0

            for link in links:

                href = link.get("href")

                if href:

                    if href.startswith("/"):
                        internal_links += 1

                    elif href.startswith("http"):
                        external_links += 1

            if internal_links > 0 or external_links > 0:
                link_score = 15
            else:
                link_score = 0

            # CONTENT LENGTH
            content_length = len(text.split())

            if content_length > 300:
                content_score = 15
            else:
                content_score = 5

            # SEO SCORE
            seo_score = (
                title_score +
                meta_score +
                h1_score +
                image_score +
                link_score +
                content_score
            )

            # SEO GRADE
            if seo_score >= 90:
                grade = "A+"
            elif seo_score >= 80:
                grade = "A"
            elif seo_score >= 70:
                grade = "B"
            elif seo_score >= 60:
                grade = "C"
            else:
                grade = "D"

            # SUGGESTIONS
            suggestions = []

            if title_score == 0:
                suggestions.append("Add a Title Tag")

            if meta_score == 0:
                suggestions.append("Add a Meta Description")

            if h1_score == 0:
                suggestions.append("Add at least one H1 Tag")

            if missing_alt > 0:
                suggestions.append(
                    f"Add ALT text to {missing_alt} image(s)"
                )

            if content_length < 300:
                suggestions.append(
                    "Increase content length"
                )

            if not suggestions:
                suggestions.append(
                    "Excellent SEO implementation"
                )

            return render_template(
                "result.html",
                title=title,
                description=description,
                h1_count=h1_count,
                image_count=image_count,
                missing_alt=missing_alt,
                internal_links=internal_links,
                external_links=external_links,
                content_length=content_length,
                seo_score=seo_score,
                grade=grade,
                response_time=response_time,
                suggestions=suggestions,
                top_keywords=top_keywords
            )

        except Exception as e:
            return f"Error: {e}"

    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)