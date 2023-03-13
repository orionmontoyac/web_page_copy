import requests
import bs4
import logging
import os

from translate import Translator

# Logs config
logger = logging.getLogger(__name__)
c_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
c_handler.setFormatter(fmt=formatter)
logger.addHandler(c_handler)
logger.setLevel(logging.DEBUG)


def group(list_, size):
    return [list_[i:i + size] for i in range(0, len(list_), size)]


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, bs4.element.Comment):
        return False
    if len(element.text) <= 2:
        return False

    return True


class HomePage:
    def __init__(self, host: str = 'https://www.classcentral.com/', file_name: str = None):
        self.host = host
        self.file_name = file_name
        self.css_link_selector = 'body main section a'
        self.html_soup = self._get_html()

    def get_links(self):
        # Select links inside the selector: body main section a
        link_elements = self.html_soup.select(self.css_link_selector)

        link_elements = [link_url['href'] for link_url in link_elements]

        # Build links
        for index, link_to_build in enumerate(link_elements):
            if 'http' not in link_to_build:
                link_elements[index] = 'https://www.classcentral.com' + link_to_build

        logger.info('Links found: {}'.format(len(link_elements)))

        return link_elements

    def _get_html(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
        response = requests.get(self.host, headers=headers)

        html_soup = bs4.BeautifulSoup(response.text, 'lxml')
        # Add JS for functionality
        script_tag = html_soup.new_tag('script', src='js/Auth.44e05080311528b179c7.js')
        html_soup.html.append(script_tag)
        script_tag = html_soup.new_tag('script', src='js/7540.b7f3ab16c1d7d344980b.js')
        html_soup.html.append(script_tag)

        logger.info('Got html for {}'.format(self.host))
        return html_soup

    def _do_translation(self):
        texts = self.html_soup.findAll(string=True)
        visible_texts = list(filter(tag_visible, texts))
        visible_texts = group(visible_texts, 40)

        for elements in visible_texts:
            texts_to_translate = [str(element) for element in elements]
            translated_texts = translator.make_translation(texts=texts_to_translate)

            for element, translated_text in zip(elements, translated_texts):
                element.string.replace_with(translated_text['translatedText'])
                # print(element.text, "->", translated_text['translatedText'])

        logger.info('Page {} translated'.format(self.file_name))

    def _save_page(self):
        path = 'web_page/' + self.file_name
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        except:
            pass

        file = open(path, 'w+')
        file.write(str(self.html_soup))
        file.close()

    def do_translation_and_save(self):
        self._do_translation()
        self._save_page()

    def main_link_internal_webpages(self):

        # Select links inside the selector: body main section a
        link_elements = self.html_soup.select('body main section a')

        for link in link_elements:
            link['href'] = link['href'].replace('https://www.classcentral.com/', '')
            # Clean link
            if link['href'][0] == '/':
                link['href'] = link['href'][1:]
            if link['href'][-1] == '/':
                link['href'] = link['href'][:-1]

            link['target'] = '_self'
            link['href'] = link['href'] + '.html'
            print(link['href'])


class InternalPage(HomePage):

    def __init__(self, host: str = None):
        super().__init__(host)
        self.host = host
        self.file_name = self._get_file_name()

    def _get_file_name(self):
        # Create file name
        file_name = self.host.replace('https://www.classcentral.com/', '')
        if file_name[-1] == '/':
            file_name = file_name[:-1] + '.html'
        else:
            file_name += '.html'

        return file_name


translator = Translator()

if __name__ == "__main__":
    # Get home page
    home_page = HomePage(file_name='index.html')
    links = home_page.get_links()
    home_page.main_link_internal_webpages()
    # Do Translation
    home_page.do_translation_and_save()

    # Get internal pages
    internal_pages = []
    for link in links:
        internal_page = InternalPage(host=link)
        internal_page.do_translation_and_save()
