from docx import Document

def load_document(file_path: str) -> str:
    """Carga el documento y extrae el texto."""
    doc = Document(file_path)
    text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
    return text

def create_chunks(text: str):
    """Divide el texto en chunks utilizando un separador y un tamaño de chunk específico."""
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n"],
        chunk_size=400,
        chunk_overlap=50,
        length_function=len
    )
    return text_splitter.split_text(text)
