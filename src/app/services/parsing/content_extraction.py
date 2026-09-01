from bs4 import BeautifulSoup
from readability import Document
 
 
def extract_title(html: str) -> str:
    return Document(html).short_title()


def extract_main_text(html:str) -> str:
    content_html = Document(html).summary()

    soup = BeautifulSoup(content_html,'lxml')
    for tag in soup(["scripts","style"]):
        tag.decompose()

    lines = [line.strip() for line in soup.get_text("\n").splitlines()]
    return "\n".join(line for line in lines if line)


