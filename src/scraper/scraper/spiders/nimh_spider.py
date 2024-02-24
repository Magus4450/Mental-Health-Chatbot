import scrapy


class NIMHSpider(scrapy.Spider):
    name = "nimh"

    def start_requests(self):
        # Urls to scrape from
        urls = [
            "https://www.nimh.nih.gov/health/topics",
            "https://www.nimh.nih.gov/health/statistics",
            "https://www.nimh.nih.gov/health/trials",
        ]

        # Apply required parsers
        for url in urls:
            if "trials" in url:
                yield scrapy.Request(url=url, callback=self.parse_trials)
            else:
                yield scrapy.Request(url=url, callback=self.parse)

        # Only single page so parse topic
        yield scrapy.Request(
            url="https://www.nimh.nih.gov/health/find-help", callback=self.parse_topic
        )

    def parse(self, response):
        # Gets differfent topics (links) and send them to parse_topic
        for topic in response.css(
            "#block-nimhtheme-content ul li a::attr(href)"
        ).getall():
            yield response.follow(topic, self.parse_topic)

    def parse_topic(self, response):
        # Title of the page
        title = response.css("#block-nimhtheme-page-title h1::text").get()

        # For each different section create a new json entry
        for section in response.css("#block-nimhtheme-content section"):
            # Get heading
            heading = section.css("h2::text").get()
            if heading is None:
                continue

            # Get text and replace non-breaking spaces
            text = "\n".join(section.css("::text").getall())
            text = text.replace("\xa0", " ")

            # Get links
            if "<a" in section.get():
                for a in section.css("a"):
                    link = a.css("a::attr(href)").get()
                    link_title = a.css("a::text").get()
                    a_title = a.css("a::attr(title)").get()
                    if a_title is not None and "Exit Disclaimer" in a_title:
                        continue

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

    def parse_trials(self, response):
        for topic in response.css(
            "section[data-cms-title='How do I find a clinical trial? '] li a[href*='/health/trials']::attr(href)"
        ).getall():
            yield response.follow(topic, self.parse_trial_topic)

    def parse_trial_topic(self, response):
        main_selector = response.css("#main_content_inner")
        main_html = main_selector.get()
        studies = main_html.split("<hr>")
        title = "Clinical Trial: " + main_selector.css("h1::text").get().replace(
            "\xa0", ""
        )

        for study in studies[1:]:
            study_selector = scrapy.Selector(text=study)
            heading = study_selector.css("h3 a::text").get().replace("\xa0", "")
            link = study_selector.css("h3 a::attr(href)").get().replace("\xa0", "")
            link = response.urljoin(link)
            link_str = f"{heading}: {link} \n"
            text = "\n".join(study_selector.css("::text").getall()).replace("\xa0", "")
            text = text.replace(heading, link_str)
            yield {
                "title": title,
                "heading": heading,
                "text": text,
            }
