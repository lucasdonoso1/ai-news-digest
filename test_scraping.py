import asyncio
import aiohttp
import bs4

async def test_scrape_news():
    AI_NEWS_SOURCES = [
        {"url": "https://artificialintelligence-news.com/", "selector": "article"},
        {"url": "https://venturebeat.com/category/ai/", "selector": "article"},
        {"url": "https://www.theverge.com/ai-artificial-intelligence", "selector": "article"}
    ]

    articles = []
    async with aiohttp.ClientSession() as session:
        for source in AI_NEWS_SOURCES:
            try:
                print(f"\nTrying to scrape: {source['url']}")
                async with session.get(source["url"]) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = bs4.BeautifulSoup(html, 'html.parser')
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
                        print(f"Error: Status code {response.status}")
            except Exception as e:
                print(f"Error scraping {source['url']}: {str(e)}")
    
    return articles

async def main():
    articles = await test_scrape_news()
    print(f"\nTotal articles found: {len(articles)}")

if __name__ == "__main__":
    asyncio.run(main())
