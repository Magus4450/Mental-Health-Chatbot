import re
from typing import Any, Optional

import scrapy


def pl(len_=50):
    print("-" * len_)


class NAMISpider(scrapy.Spider):
    def __init__(self, **kwargs: Any):
        self.debug = True
        super().__init__(**kwargs)

    name = "nami"

    def start_requests(self):
        # Urls to scrape from
        urls = ["https://www.nami.org/About-Mental-Illness/Warning-Signs-and-Symptoms"]

        # Apply required parsers
        for url in urls:
            if self.debug:
                pl()
                print("URL: ", url)
                pl()

            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        print("Parsing links")
        links = response.css(".side-navigation li a::attr(href)").getall()
        print(f"Got {len(links)} links")
        mental_health_condition_info = links[1:2]
        mental_health_condition = links[2:16]
        common_with_mental_health_info = links[16:17]
        common_with_mental_health = links[17:26]
        treatments_info = links[26:27]
        treatments = links[27:123]
        mh_fact = links[124:125]
        research_info = links[126:127]
        research = links[127:137]

        pl()
        print(
            f"Crawling through {len(mental_health_condition)} mental health conditions links"
        )
        pl()
        for url in mental_health_condition + common_with_mental_health:
            # if .tabs-mental
            urls_addons = {
                "overview-tab": "",
                "treatment-tab": "Treatment",
                "support-tab": "Support",
            }
            for k, v in urls_addons.items():
                url_new = url + f"/{v}"
                print(f"Scraping {url_new}")
                yield response.follow(
                    url_new,
                    self.parse_mental_health_condition,
                    meta={"tab": k},
                )

    def parse_mental_health_condition(self, response):
        tab = response.meta.get("tab")

        if response.css(".tabs-mental").get() is None:
            if tab == "overview-tab":
                tab = "rightRailNavigation"
            else:
                return

        print("Getting title")
        title = response.css(".page-title::text").get()
        if tab != "rightRailNavigation":
            title = f"{title} {tab.split('-')[0].capitalize()}"
        print("Getting main content using tab", tab)
        content = response.css(f".{tab}")
        content_html = content.get()

        if content_html is None:
            # It means that there is not tabs
            print("No content found")
            print("URL", response.url)
            print("TAB", tab)
            pl()
            pl()
            pl()
            return
        content_html = content_html.replace("\xa0", "")

        print("Finding all h2s")
        pattern = r"<h2>(.*?)<\/h2>"
        matches = re.findall(pattern, content_html)
        print(f"Found {len(matches)} h2s")

        for i in range(len(matches) + 1):
            pl(10)
            print(f"Getting section {i} of {len(matches)}")
            start_search = f"<h2>{matches[i-1]}</h2>" if i > 0 else ""
            end_search = f"<h2>{matches[i]}</h2>" if i < len(matches) else ""
            start_search = start_search.replace("(", "\(").replace(")", "\)")
            end_search = end_search.replace("(", "\(").replace(")", "\)")
            mid_search = "(.*?)" if i < len(matches) else ".*"
            search_query = f"{start_search}{mid_search}{end_search}"
            print(f"Search query: {search_query}")
            search_query = search_query

            result = re.search(search_query, content_html, re.DOTALL)
            heading = matches[i - 1] if i > 0 else "Information"

            try:
                if i == len(matches):
                    out = result.group(0)
                else:
                    out = result.group(1)
            except Exception as e:
                pl(50)
                print("ERROR GETTING A MATCH")
                pl(50)
                print(e)
                return

            selector = scrapy.Selector(text=out)

            text = "\n".join(selector.css("::text").getall()).replace("\xa0", "")

            if "<a" in selector.get():
                for a in selector.css("a"):
                    link = a.css("a::attr(href)").get()
                    link_title = a.css("a::text").get()

                    # Need to do this for infinite loops
                    if (
                        link is None
                        or link_title is None
                        or link_title.isspace()
                        or link_title == ""
                    ):
                        continue

                    link = link.replace("\xa0", "")
                    link_title = link_title.replace("\xa0", "")

                    # Convert link to absolute URL
                    if not link.startswith("http"):
                        abs_link = response.urljoin(link)
                    else:
                        abs_link = link

                    link_str = f"{link_title}: {abs_link} \n"

                    # Replace
                    text = text.replace(link_title, link_str)
            yield {
                "title": title,
                "heading": heading,
                "text": text,
            }
            pl(10)
