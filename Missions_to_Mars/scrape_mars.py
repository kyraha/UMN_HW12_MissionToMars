# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from bs4 import BeautifulSoup
from splinter import Browser
import requests
import time
import pandas as pd

#%%
def scrape():
    # URL of page to be scraped
    news_url = "https://mars.nasa.gov/news/"
    scraped_data = {}


    # %%
    # Splinter Chrome driver is initialized here. This code is very platform or even host dependent. So I isolate it here to instantiate the browser once for the entire notebook and will use the same instance further down.
    browser = Browser('chrome', {'executable_path': '/usr/bin/chromdriver'}, headless=False)


    # %% [markdown]
    # ## Splinter version
    # It looks like the NASA news site uses dynamic content loading. So simple `requests` is too static for the task. Let's load the page in a real web browser and redo the soup.

    # %%
    # Open the URL in the browser
    browser.visit(news_url)
    # Wait for a while to let the browser load the content and render the news
    time.sleep(2.0)
    # After the sleep now the time to grab the rendered html
    html = browser.html


    # %%
    # Create BeautifulSoup object; parse with 'html.parser'
    soup = BeautifulSoup(html, 'html.parser')
    # results are returned as an iterable list
    results = soup.find_all('div', class_="list_text")


    # %%
    # Store all the news in a list
    news = []

    # Traverse through the results to extract titles and teasers
    for result in results:
        try:
            # Each item in the news list is a dictionary
            item = {}
            # Identify and return teaser of the news
            item['news_p'] = result             .find("div", class_="article_teaser_body")             .text.strip()
            # Identify and return title of the news
            item['news_title'] = result             .find("div", class_="content_title")             .find("a").text.strip()
            item['news_date'] = result             .find("div", class_="list_date")             .text.strip()
            # Store the newly constructed news item in the list of news
            news.append(item)
        except AttributeError as e:
            print(e)

    # # See what we have gathered
    # for item in news:
    #     print("Date:  ", item['news_date'])
    #     print("Title: ", item['news_title'])
    #     print("Teaser:", item['news_p'])
    #     print("")
    scraped_data['news_title'] = news[0]['news_title']
    scraped_data['news_p'] = news[0]['news_p']

    # %% [markdown]
    # ## JPL Mars Space Images - Featured Image
    # The challenge is to click a button on the page to activate a pop-up window (a "fancy box") with the featured image and extract the source URL of that image.

    # %%
    # URL of page to be scraped
    space_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    # Retrieve page with the requests module
    space_html = browser.visit(space_url)
    time.sleep(2.0)
    img_button = browser.find_by_id('full_image').first


    # %%
    img_button.click()
    time.sleep(2.0)
    fancy_image = browser.find_by_css('.fancybox-image').first
    featured_image_url = fancy_image['src']
    browser.find_by_css('a.fancybox-close').click()

    scraped_data['featured_image_url'] = featured_image_url

    # %% [markdown]
    # ## Mars Weather
    # https://twitter.com/marswxreport?lang=en
    # 

    # %%
    browser.visit("https://twitter.com/marswxreport?lang=en")
    time.sleep(2.0)
    weather_html = browser.html


    # %%
    # Create BeautifulSoup object; parse with 'html.parser'
    InSight_soup = BeautifulSoup(weather_html, 'html.parser')
    # results are returned as an iterable list
    InSight_spans = InSight_soup.find_all('span')


    # %%
    # Twit texts are buried deep in div hierarchy. However the text paragraphs are within span tags. And the twits we're looking for are all start with "InSight sol" and then the sol number. The latest is on the top of the list. So all we have to do is to find the first entry matching these criteria.

    # Define mars_weather variable and initialize it with "Not found" string so in case if the wether twit is not found we will see that that was the case.
    mars_weather = "Not found."

    # Iterate through all spans on the page looking for specific string as the first 12 characters
    for span in InSight_spans:
        if span.text[:12] == "InSight sol ":
            mars_weather = span.text[7:]
            # Break the loop as soon as we find the first match
            break

    scraped_data['mars_weather'] = mars_weather

    # %% [markdown]
    # ## Mars Facts
    # 
    # * Visit the Mars Facts webpage at https://space-facts.com/mars/ and use Pandas to scrape the table containing facts about the planet including Diameter, Mass, etc.
    # * Use Pandas to convert the data to a HTML table string.

    # %%
    tables = pd.read_html("https://space-facts.com/mars/")
    fact_table = tables[0]
    fact_table.columns = ["Fact", "Value"]
    fact_table.set_index("Fact", inplace=True)


    # %%
    fact_table_html = fact_table.to_html()

    scraped_data['fact_table_html'] = fact_table_html

    # %% [markdown]
    # ## Mars Hemispheres
    # https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars

    # %%
    browser.visit("https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars")
    hemi_html = browser.html


    # %%
    hemisphere_image_urls = []
    results = BeautifulSoup(hemi_html, 'html.parser').find("div", class_="results")
    for item in results.find_all("div", class_="item"):
        title = item.find("div", class_="description").a.text
        browser.find_link_by_partial_text(title).first.click()
        original_img = browser.find_link_by_partial_text("Sample").first.outer_html
        img_url = BeautifulSoup(original_img, 'html.parser').find('a')['href']
        browser.back()
        hemisphere_image_urls.append({
            "title": title,
            "img_url": img_url
        })

    scraped_data['hemisphere_image_urls'] = hemisphere_image_urls

    # %%
    browser.quit()
    return scraped_data
