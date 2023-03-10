import requests
import bs4
import glob
import os
"""
<script src="js/UserActions.30ee83ef27eafec0be61.js"></script>
<script src="js/MarkComplete.e9560adcebc4ad54e6bf.js"></script>
<script src="js/Auth.44e05080311528b179c7.js"></script>

<script src="js/Misc.a66f8a686e276f997313.js"></script>
<script src="js/4826.ea570b7100e8c5e53e11.js"></script>
<script src="js/7540.b7f3ab16c1d7d344980b.js"></script>
"""

from translate import Translator


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


def text_translation_from_html(html_soup):
    translator = Translator()

    texts = html_soup.findAll(string=True)
    visible_texts = list(filter(tag_visible, texts))

    visible_texts = group(visible_texts, 40)

    for elements in visible_texts:
        texts_to_translate = [str(element) for element in elements]
        translated_texts = translator.make_translation(texts=texts_to_translate)

        for element, translated_text in zip(elements, translated_texts):
            element.string.replace_with(translated_text['translatedText'])
            # print(element.text, "->", translated_text['translatedText'])

    print('Groups translated: ', len(visible_texts))

    return html_soup


def get_html_code(host_url: str):
    print("Getting HTML code for: ", host_url)

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
    response = requests.get(host_url, headers=headers)

    return bs4.BeautifulSoup(response.text, 'html.parser')


def get_links(html_soup: bs4.BeautifulSoup):
    # Select links inside the selector: body main section a
    links = html_soup.select('body main section a')

    links = [link_url['href'] for link_url in links]

    # Build links
    for index, link_to_build in enumerate(links):
        if 'http' not in link_to_build:
            links[index] = 'https://www.classcentral.com' + link_to_build

    return links


def save_web_page(html, file_name):
    # Save web page to file
    # Create folder if necessary
    if 'web_page' not in file_name:
        file_name = 'web_page/' + file_name

    try:
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
    except:
        pass

    file = open(file_name, 'w+')
    file.write(str(html))
    file.close()


def open_html_file(file_name):
    with open(file_name, "r", encoding='utf-8') as f:
        text = f.read()
        return text


def web_scrapper():
    # Get the home page
    host = 'https://www.classcentral.com/'
    html = get_html_code(host_url=host)

    # Add JS for functionality
    script_tag = html.new_tag('script', src='js/Auth.44e05080311528b179c7.js')
    html.html.append(script_tag)
    script_tag = html.new_tag('script', src='js/7540.b7f3ab16c1d7d344980b.js')
    html.html.append(script_tag)

    # Save home page
    save_web_page(html, 'index.html')

    # Get the links from the home page
    elements_links = get_links(html)

    for i, link in enumerate(elements_links, start=1):
        print(i, link)
        # Getting html code for internal page
        html = get_html_code(link)
        # Create file name
        file_name = link.replace('https://www.classcentral.com/','')
        if file_name[-1] == '/':
            file_name = file_name[:-1] + '.html'
        else:
            file_name += '.html'

        # Save web page to file
        save_web_page(html, file_name)


def main_link_internal_webpages():
    text = open_html_file('web_page/index.html')

    html_soup = bs4.BeautifulSoup(text, 'html.parser')
    # Select links inside the selector: body main section a
    links = html_soup.select('body main section a')

    for link in links:
        link['href'] = link['href'].replace('https://www.classcentral.com/','')
        # Clean link
        if link['href'][0] == '/':
            link['href'] = link['href'][1:]
        if link['href'][-1] == '/':
            link['href'] = link['href'][:-1]

        link['target'] = '_self'
        link['href'] = link['href'] + '.html'
        print(link['href'])

    save_web_page(html_soup, 'index.html')


if __name__ == "__main__":
    # Get html code from the website
    web_scrapper()

    # Link local web pages to index.html
    main_link_internal_webpages()

    # Translate de documents
    html_files = glob.glob('web_page/**/*.html', recursive=True)

    for html_file in html_files:
        print('Page to translate: ', html_file)
        text = open_html_file(html_file)
        html = bs4.BeautifulSoup(text, 'html.parser')
        html_translation = text_translation_from_html(html)
        save_web_page(html_translation, file_name=html_file)
