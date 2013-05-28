# Copyright (c) Sunlight Labs, 2013, under the terms of the BSD-3 clause
# license.
#
#  Contributors:
#
#    - Paul Tagliamonte <paultag@sunlightfoundation.com>


from pupa.scrape import Scraper
from larvae.event import Event

import datetime as dt
import lxml.html


class NewYorkCityEventsScraper(Scraper):

    def lxmlize(self, url, encoding='utf-8'):
        entry = self.urlopen(url).encode(encoding)
        page = lxml.html.fromstring(entry)
        page.make_links_absolute(url)
        return page


    def get_events(self):
        url = "http://legistar.council.nyc.gov/Calendar.aspx"
        page = self.lxmlize(url)
        main = page.xpath("//table[@class='rgMasterTable']")[0]
        rows = main.xpath(".//tr")[1:]
        for row in rows:
            (name, date, time, where, topic,
             details, agenda, minutes, media) = row.xpath(".//td")

            name = name.text_content().strip()  # leaving an href on the table
            time = time.text_content().strip()
            location = where.text_content().strip()
            topic = topic.text_content().strip()

            if "Deferred" in time:
                continue

            all_day = False
            if time == "":
                all_day = True
                when = dt.datetime.strptime(date.text.strip(),
                                            "%m/%d/%Y")
            else:
                when = dt.datetime.strptime("%s %s" % (date.text.strip(), time),
                                            "%m/%d/%Y %I:%M %p")

            event = Event(description=name,
                          start=when,
                          location=location)
            event.add_source(url)

            details = details.xpath(".//a[@href]")
            for detail in details:
                event.add_document(detail.text, detail.attrib['href'])

            agendas = agenda.xpath(".//a[@href]")
            for a in agendas:
                event.add_document(a.text, a.attrib['href'])

            minutes = minutes.xpath(".//a[@href]")
            for minute in minutes:
                event.add_document(minute.text, minute.attrib['href'])

            yield event
