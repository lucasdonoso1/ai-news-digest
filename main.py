import os
import logging
from fastapi import FastAPI, HTTPException
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()
scheduler = AsyncIOScheduler()

AI_NEWS_SOURCES = [
    {"url": "https://artificialintelligence-news.com/", "selector": "article"},
    {"url": "https://venturebeat.com/category/ai/", "selector": "article"},
    {"url": "https://www.theverge.com/ai-artificial-intelligence", "selector": "article"}
]

def scrape_news():
    articles = []
    for source in AI_NEWS_SOURCES:
        try:
            logger.info(f"Scraping: {source['url']}")
            response = requests.get(source["url"])
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                found_articles = soup.select(source["selector"])
                logger.info(f"Found {len(found_articles)} articles from {source['url']}")
                
                for article in found_articles[:3]:
                    title = article.find(['h1', 'h2', 'h3'])
                    if title:
                        title_text = title.text.strip()
                        articles.append({
                            'title': title_text,
                            'source': source["url"]
                        })
                        logger.info(f"Found article: {title_text}")
            else:
                logger.error(f"Error: Status code {response.status_code} from {source['url']}")
        except Exception as e:
            logger.error(f"Error scraping {source['url']}: {str(e)}")
    
    return articles

def send_digest_email(recipient_email: str):
    try:
        articles = scrape_news()
        
        if not articles:
            logger.warning("No articles found to send")
            return
        
        email_content = "Today's AI News Digest:\n\n"
        for article in articles:
            email_content += f"• {article['title']}\n  Source: {article['source']}\n\n"
        
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = os.getenv('GMAIL_EMAIL')
        msg['To'] = recipient_email
        msg['Subject'] = f'AI News Digest - {datetime.now().strftime("%Y-%m-%d")}'
        msg.attach(MIMEText(email_content, 'plain'))
        
        # Connect to Gmail SMTP server
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            gmail_email = os.getenv('GMAIL_EMAIL')
            gmail_password = os.getenv('GMAIL_APP_PASSWORD')
            
            if not gmail_email or not gmail_password:
                raise ValueError("Gmail credentials not properly configured")
                
            server.login(gmail_email, gmail_password)
            server.send_message(msg)
            logger.info(f"Email sent successfully to {recipient_email}")
            
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup_event():
    try:
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
        logger.info("Scheduler started successfully")
    except Exception as e:
        logger.error(f"Error in startup: {str(e)}")
        raise

@app.get("/")
async def root():
    return {
        "status": "running",
        "message": "AI News Digest Service is active",
        "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

@app.get("/test")
async def test_digest():
    try:
        recipient_email = os.getenv('RECIPIENT_EMAIL')
        if not recipient_email:
            raise HTTPException(status_code=500, detail="RECIPIENT_EMAIL not set")
        
        send_digest_email(recipient_email)
        return {
            "status": "success",
            "message": f"Test digest email sent to {recipient_email}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        logger.error(f"Error in test endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
