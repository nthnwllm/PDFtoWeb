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

    # Add the CSS link
    link = soup.new_tag('link', rel="stylesheet", href="../../style.css")
    head.append(link)
    link = soup.new_tag('link', rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap")
    head.append(link)

    # Add the header with the chapter number using a special class
    header = soup.new_tag('header')
    header_h1 = soup.new_tag('h1', **{'class': 'chapter-header'})
    header_h1.string = f"Chapter {chapter_num}"
    header.append(header_h1)
    body.append(header)

    # Add the hamburger menu
    hamburger_html = """
    <!-- Hamburger Menu Icon -->
    <button class="nav-toggle" aria-label="toggle navigation">
        <span class="hamburger"></span>
    </button>

    <!-- Collapsible Sidebar Menu -->
    <nav class="nav-mobile">
        <ul class="nav-mobile__list">
    """

    # Add chapter links to the hamburger menu
    for i in range(1, total_chapters + 1):
        hamburger_html += f'<li class="nav-mobile__item"><a href="chapter_{i}.html" class="nav-mobile__link">Chapter {i}</a></li>'

    hamburger_html += """
        </ul>
    </nav>
    """

    body.append(BeautifulSoup(hamburger_html, 'html.parser'))

    # Add the content to the body
    for content in chapter_content:
        body.append(BeautifulSoup(content, 'html.parser'))

    # Add navigation buttons
    nav = soup.new_tag('div', **{'class': 'navigation'})
    if chapter_num > 1:
        prev_link = soup.new_tag('a', href=f'chapter_{chapter_num - 1}.html', **{'class': 'prev'})
        prev_link.string = "Previous"
        nav.append(prev_link)

    if chapter_num < total_chapters:
        next_link = soup.new_tag('a', href=f'chapter_{chapter_num + 1}.html', **{'class': 'next'})
        next_link.string = "Next"
        nav.append(next_link)

    body.append(nav)

    # Add footer with eBook details
    footer = soup.new_tag('footer')
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
                                chapter_content.append(f"<h1>{text}</h1>")
                            elif span["size"] > 12 and span["flags"] == 20:  # Heading 2: Medium & Bold
                                chapter_content.append(f"<h2>{text}</h2>")
                            else:
                                # Paragraph detection
                                if len(chapter_content) > 0 and block["bbox"][1] - prev_block_bottom > 12:  # Example threshold
                                    chapter_content.append("<br>")
                                chapter_content.append(f"<p>{text}</p>")
                                prev_block_bottom = block["bbox"][3]

        # Convert the collected content to HTML
        convert_text_to_html(chapter_content, output_dir, chapter_num, total_chapters)

def main():
    pdf_path = "D:/projects/python_projects/PDFtoWeb/the_case_for_christ.pdf"
    output_dir = "D:/projects/python_projects/PDFtoWeb/books/the_case_for_christ"
    os.makedirs(output_dir, exist_ok=True)

    # Define the number of pages per chapter
    pages_per_chapter = 5  # You can adjust this

    # Process the PDF in chunks, converting to HTML as we go
    process_pdf_in_chunks(pdf_path, output_dir, pages_per_chapter)

if __name__ == "__main__":
    main()