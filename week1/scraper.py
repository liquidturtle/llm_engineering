from bs4 import BeautifulSoup
import requests


# Standard headers to fetch a website
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}


def fetch_website_contents(url):
    """
    Return the title and contents of the website at the given url;
    truncate to 2,000 characters as a sensible limit.
    Uses simple requests + BeautifulSoup (no JavaScript execution).
    """
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    title = soup.title.string if soup.title else "No title found"

    if soup.body:
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        text = soup.body.get_text(separator="\n", strip=True)
    else:
        text = ""

    return (title + "\n\n" + text)[:2_000]


def fetch_website_links(url):
    """
    Return the links on the website at the given url.
    NOTE: This makes a separate request from fetch_website_contents
    to keep the code simple for teaching purposes.
    """
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    links = [link.get("href") for link in soup.find_all("a")]
    return [link for link in links if link]


def fetch_website_contents_selenium(url, driver=None, close_driver=False):
    """
    Use Selenium to render the page (JS included), then parse with BeautifulSoup.
    Returns the title and contents of the website at the given url;
    truncated to 2,000 characters.
    
    Parameters
    ----------
    url : str
        URL to fetch.
    driver : selenium.webdriver, optional
        Existing Selenium WebDriver instance. If None, a temporary
        headless Chrome driver will be created (requires selenium + driver binary).
    close_driver : bool, default False
        If True and a driver was created inside this function, it will be quit.
        Ignored if an external driver is passed in.

    Notes
    -----
    - Many modern sites use bot protection (e.g. “Just a moment... / enable JS and cookies”).
      In those cases, even Selenium may only see that intermediate page instead of the
      real content, especially in headless mode.
    - This function improves the browser fingerprint slightly (User-Agent) and waits
      for the body to load, which helps on simpler sites but does not bypass serious
      anti-bot measures.
    """
    created_local_driver = False

    if driver is None:
        # Lazy import so selenium is only required when this function is used
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        import time

        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # Use the same User-Agent as our requests-based fetch
        options.add_argument(f"user-agent={headers['User-Agent']}")

        driver = webdriver.Chrome(options=options)
        created_local_driver = True

    try:
        driver.get(url)

        # Optional: wait a bit for JS-heavy pages; tweak as needed or use WebDriverWait
        driver.implicitly_wait(5)

        # A small extra sleep can help slow-loading JS pages (kept minimal for teaching)
        import time
        time.sleep(2)

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        title = soup.title.string if soup.title else "No title found"

        if soup.body:
            for irrelevant in soup.body(["script", "style", "img", "input"]):
                irrelevant.decompose()
            text = soup.body.get_text(separator="\n", strip=True)
        else:
            text = ""

        return (title + "\n\n" + text)[:2_000]
    finally:
        if created_local_driver and close_driver:
            driver.quit()
