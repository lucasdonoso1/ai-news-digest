import os
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import aiohttp
import bs4
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
scheduler = AsyncIOScheduler()

AI_NEWS_SOURCES = [
    {"url": "https://artificialintelligence-news.com/", "selector": "article"},
    {"url": "https://venturebeat.com/category/ai/", "selector": "article"},
    {"url": "https://www.theverge.com/ai-artificial-intelligence", "selector": "article"}
]

async def scrape_news():
    articles = []
    async with aiohttp.ClientSession() as session:
        for source in AI_NEWS_SOURCES:
            try:
                async with session.get(source["url"]) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = bs4.BeautifulSoup(html, 'html.parser')
                        for article in soup.select(source["selector"])[:3]:
                            title = article.find(['h1', 'h2', 'h3'])
                            if title:
                                articles.append({
                                    'title': title.text.strip(),
                                    'source': source["url"]
                                })
            except Exception as e:
                print(f"Error scraping {source['url']}: {str(e)}")
    return articles

async def send_digest_email(recipient_email: str):
    articles = await scrape_news()
    
    if not articles:
        return
    
    email_content = "Today's AI News Digest:\n\n"
    for article in articles:
        email_content += f"• {article['title']}\n  Source: {article['source']}\n\n"
    
    message = Mail(
        from_email=os.getenv('SENDGRID_FROM_EMAIL'),
        to_emails=recipient_email,
        subject=f'AI News Digest - {datetime.now().strftime("%Y-%m-%d")}',
        plain_text_content=email_content
    )
    
    try:
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(f"Email sent successfully: {response.status_code}")
    except Exception as e:
        print(f"Error sending email: {str(e)}")

@app.on_event("startup")
async def startup_event():
    recipient_email = os.getenv('RECIPIENT_EMAIL')
    if not recipient_email:
        raise ValueError("RECIPIENT_EMAIL environment variable is not set")
    
    # Schedule daily digest at 9:00 AM CET
    scheduler.add_job(
        send_digest_email,
        CronTrigger(hour=9, minute=0, timezone='Europe/Paris'),
        args=[recipient_email]
    )
    scheduler.start()

@app.get("/")
async def root():
    return {"status": "running", "message": "AI News Digest Service is active"}
