# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt

# Set the executable path and initialize the chrome browser in splinter
def scrape_all():
    #executable_path = {'executable_path': 'chromedriver.exe'}
    #browser = Browser('chrome', **executable_path)
    browser = Browser("chrome", executable_path="chromedriver", headless=True)
    news_title, news_paragraph = mars_news(browser)
    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "details":details(browser)
    }
    browser.quit()
    return data


# News Articles


def mars_news(browser):
    url='https://mars.nasa.gov/news/'
    browser.visit(url)
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)
    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')
    try:
        slide_elem = news_soup.select_one('ul.item_list li.slide')
        news_title = slide_elem.find("div", class_='content_title').get_text()
        news_p = slide_elem.find('div', class_="article_teaser_body").get_text()
        return news_title, news_p
    except AttributeError:
        return None, None



# ### Featured Images
def featured_image(browser):
    url='https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.find_link_by_partial_text('more info')
    more_info_elem.click()
    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')
    try:
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")
        img_url = f'https://www.jpl.nasa.gov{img_url_rel}'
        return img_url
    except AttributeError:
        return None

def details(browser):
    url_root = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url_root)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    sections = soup.find('div', class_='full-content').find_all('div', class_='item')
    links = []
    for i in range(0, 4):
        links.append("https://astrogeology.usgs.gov/"+sections[i].find('a', href=True)['href'])
    
    details=[]
    for link in links:
        url = link
        browser.visit(url)
        html = browser.html
        soup = BeautifulSoup(html, 'html.parser')
        try:
            find_link = "https://astrogeology.usgs.gov/" + soup.find('div', class_='container').find('div', id='wide-image').find('img', class_='wide-image').get('src')
            find_title = soup.find('div', class_='container').find('div', class_='content').find('section', class_='block metadata').find('h2', class_='title').get_text()
            details.append({"title":find_title,"img_url":find_link})
        except AttributeError:
            pass

    return details

def mars_facts():
    try:
        df = pd.read_html('http://space-facts.com/mars/')[0]
    except BaseException:
        return None
        
    df.columns=['description', 'value']
    df.set_index('description', inplace=True)
    return df.to_html() 

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())