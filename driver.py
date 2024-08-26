import fitz  # PyMuPDF
from bs4 import BeautifulSoup
import os

def convert_text_to_html(chapter_content, output_dir, chapter_num, total_chapters):
    # Create a BeautifulSoup object
    soup = BeautifulSoup("", 'html.parser')

    # Create basic HTML structure
    html = soup.new_tag('html')
    head = soup.new_tag('head')
    body = soup.new_tag('body')
    soup.append(html)
    html.append(head)
    html.append(body)

    # Add CSS and fonts
    link_css = soup.new_tag('link', href='../../style.css', rel='stylesheet')
    link_fonts = soup.new_tag('link', href='https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap', rel='stylesheet')
    link_font_awesome = soup.new_tag('link', href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css', rel='stylesheet', integrity="sha512-Kc323vGBEqzTmouAECnVceyQqyqdsSiqLQISBL29aUW4U/M7pSPA/gEUZQqv1cwx4OnYxTxve5UMg5GT6L4JJg==", crossorigin="anonymous", referrerpolicy="no-referrer")

    head.append(link_css)
    head.append(link_fonts)
    head.append(link_font_awesome)

    # Add the header with the hamburger menu, sidebar, and home button
    header = soup.new_tag('header')

    # Hamburger menu
    nav_toggle = soup.new_tag('button', **{'aria-label': 'toggle navigation', 'class': 'nav-toggle'})
    hamburger_span = soup.new_tag('span', **{'class': 'hamburger'})
    nav_toggle.append(hamburger_span)
    header.append(nav_toggle)

    # Sidebar navigation menu
    nav_mobile = soup.new_tag('nav', **{'class': 'nav-mobile', 'aria-hidden': 'true'})
    nav_list = soup.new_tag('ul', **{'class': 'nav-mobile__list'})

    for i in range(1, total_chapters + 1):
        nav_item = soup.new_tag('li', **{'class': 'nav-mobile__item'})
        nav_link = soup.new_tag('a', href=f'chapter_{i}.html', **{'class': 'nav-mobile__link'})
        nav_link.string = f'Chapter {i}'
        nav_item.append(nav_link)
        nav_list.append(nav_item)

    nav_mobile.append(nav_list)
    header.append(nav_mobile)

    # Home button
    home_button = soup.new_tag('a', href='../../index.html', **{'class': 'logo'})
    home_icon = soup.new_tag('i', **{'class': 'fa-solid fa-book'})
    home_button.append(home_icon)
    header.append(home_button)

    body.append(header)

    # Add chapter header
    chapter_header = soup.new_tag('h1', **{'class': 'chapter-header'})
    chapter_header.string = f"Chapter {chapter_num}"
    body.append(chapter_header)

    # Add the content to the body
    for content in chapter_content:
        body.append(BeautifulSoup(content, 'html.parser'))

    # Add navigation buttons
    nav = soup.new_tag('div', **{'class': 'navigation'})
    if chapter_num > 1:
        prev_link = soup.new_tag('a', href=f'chapter_{chapter_num - 1}.html', **{'class': 'prev', 'aria-hidden': 'true'})
        prev_link.string = "Previous"
        nav.append(prev_link)

    if chapter_num < total_chapters:
        next_link = soup.new_tag('a', href=f'chapter_{chapter_num + 1}.html', **{'class': 'next', 'aria-hidden': 'true'})
        next_link.string = "Next"
        nav.append(next_link)

    body.append(nav)

    # Add footer with eBook details
    footer = soup.new_tag('footer', **{'aria-hidden': 'true'})
    footer.append(BeautifulSoup("<p>Author: Lee Strobel</p>", 'html.parser'))
    footer.append(BeautifulSoup("<p>Published: 1998</p>", 'html.parser'))
    footer.append(BeautifulSoup("<p>ISBN: 978-0310226469</p>", 'html.parser'))
    body.append(footer)

    # Add the JavaScript link
    script = soup.new_tag('script', src="../../script.js")
    body.append(script)

    # Save the HTML file
    file_path = os.path.join(output_dir, f'chapter_{chapter_num}.html')
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(soup.prettify())

    print(f"Chapter {chapter_num} saved as {file_path}")

def process_pdf_in_chunks(pdf_path, output_dir, pages_per_chapter):
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    total_chapters = (total_pages + pages_per_chapter - 1) // pages_per_chapter


    for start_page in range(0, total_pages, pages_per_chapter):
        chapter_content = []
        prev_block_bottom = 0
        paragraph = ""
        chapter_num = (start_page // pages_per_chapter) + 1
        for page_num in range(start_page, min(start_page + pages_per_chapter, total_pages)):
            page = doc.load_page(page_num)
            blocks = page.get_text("dict")["blocks"]  # Get text blocks with details

            for block in blocks:
                if "lines" not in block:
                    continue

                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if text:
                            # Heading and paragraph detection
                            if span["size"] > 15 and span["flags"] == 20:  # Heading 1: Large & Bold
                                if paragraph:
                                    chapter_content.append(f"<p>{paragraph}</p>")
                                    paragraph = ""
                                chapter_content.append(f"<h1>{text}</h1>")
                            elif span["size"] > 12 and span["flags"] == 20:  # Heading 2: Medium & Bold
                                if paragraph:
                                    chapter_content.append(f"<p>{paragraph}</p>")
                                    paragraph = ""
                                chapter_content.append(f"<h2>{text}</h2>")
                            else:
                                # If there's a significant vertical gap, start a new paragraph
                                if len(chapter_content) > 0 and block["bbox"][1] - prev_block_bottom > 12:  # Example threshold
                                    if paragraph:
                                        chapter_content.append(f"<p>{paragraph}</p>")
                                    chapter_content.append("<br>")
                                    paragraph = text
                                else:
                                    paragraph += " " + text
                                prev_block_bottom = block["bbox"][3]
        if paragraph:
            chapter_content.append(f"<p>{paragraph}</p>")

        # Convert the collected content to HTML
        convert_text_to_html(chapter_content, output_dir, chapter_num, total_chapters)

def main():
    # Change the PDF path according to what book you're trying to convert to Web form:
    pdf_path = "D:/projects/python_projects/PDFtoWeb/the_case_for_christ.pdf" 
    output_dir = "D:/projects/python_projects/PDFtoWeb/books/the_case_for_christ"
    os.makedirs(output_dir, exist_ok=True)

    # Define the number of pages per chapter
    pages_per_chapter = 5  # You can adjust this

    # Process the PDF in chunks, converting to HTML as we go
    process_pdf_in_chunks(pdf_path, output_dir, pages_per_chapter)

if __name__ == "__main__":
    main()