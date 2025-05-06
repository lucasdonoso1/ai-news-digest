import os
import requests
import smtplib
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def scrape_news():
    AI_NEWS_SOURCES = [
        {"url": "https://artificialintelligence-news.com/", "selector": "article"},
        {"url": "https://venturebeat.com/category/ai/", "selector": "article"},
        {"url": "https://www.theverge.com/ai-artificial-intelligence", "selector": "article"}
    ]

    articles = []
    for source in AI_NEWS_SOURCES:
        try:
            print(f"\nTrying to scrape: {source['url']}")
            response = requests.get(source["url"])
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                found_articles = soup.select(source["selector"])
                print(f"Found {len(found_articles)} articles")
                
                for article in found_articles[:3]:
                    title = article.find(['h1', 'h2', 'h3'])
                    if title:
                        title_text = title.text.strip()
                        articles.append({
                            'title': title_text,
                            'source': source["url"]
                        })
                        print(f"Found article: {title_text}")
            else:
                print(f"Error: Status code {response.status_code}")
        except Exception as e:
            print(f"Error scraping {source['url']}: {str(e)}")
    
    return articles

def send_email(articles):
    if not articles:
        print("No articles to send")
        return
    
    email_content = "Today's AI News Digest:\n\n"
    for article in articles:
        email_content += f"• {article['title']}\n  Source: {article['source']}\n\n"
    
    msg = MIMEMultipart()
    msg['From'] = os.getenv('GMAIL_EMAIL')
    msg['To'] = os.getenv('RECIPIENT_EMAIL')
    msg['Subject'] = "Test AI News Digest"
    msg.attach(MIMEText(email_content, 'plain'))
    
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(os.getenv('GMAIL_EMAIL'), os.getenv('GMAIL_APP_PASSWORD'))
            server.send_message(msg)
            print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {str(e)}")

if __name__ == "__main__":
    print("Starting test...")
    articles = scrape_news()
    print(f"\nTotal articles found: {len(articles)}")
    if articles:
        print("\nSending email...")
        send_email(articles)
    else:
        print("No articles found to send")
