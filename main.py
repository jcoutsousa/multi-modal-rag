from langchain_text_splitters import CharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from loadfiles import extract_pdf_elements, categorize_elements
from imgproc import generate_img_summaries
from retrieval import  generate_text_summaries
from addvectorstore import Chroma, OpenAIEmbeddings,create_multi_vector_retriever

from langchain_core.documents import Document


import io
import re

from IPython.display import HTML, display
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from PIL import Image

#Images summaries
import base64
import os

from langchain_core.messages import HumanMessage


def plt_img_base64(img_base64):
    """Disply base64 encoded string as image"""
    # Create an HTML img tag with the base64 string as the source
    image_html = f'<img src="data:image/jpeg;base64,{img_base64}" />'
    # Display the image by rendering the HTML
    display(HTML(image_html))


def looks_like_base64(sb):
    """Check if the string looks like base64"""
    return re.match("^[A-Za-z0-9+/]+[=]{0,2}$", sb) is not None


def is_image_data(b64data):
    """
    Check if the base64 data is an image by looking at the start of the data
    """
    image_signatures = {
        b"\xff\xd8\xff": "jpg",
        b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a": "png",
        b"\x47\x49\x46\x38": "gif",
        b"\x52\x49\x46\x46": "webp",
    }
    try:
        header = base64.b64decode(b64data)[:8]  # Decode and get the first 8 bytes
        for sig, format in image_signatures.items():
            if header.startswith(sig):
                return True
        return False
    except Exception:
        return False


def resize_base64_image(base64_string, size=(128, 128)):
    """
    Resize an image encoded as a Base64 string
    """
    # Decode the Base64 string
    img_data = base64.b64decode(base64_string)
    img = Image.open(io.BytesIO(img_data))

    # Resize the image
    resized_img = img.resize(size, Image.LANCZOS)

    # Save the resized image to a bytes buffer
    buffered = io.BytesIO()
    resized_img.save(buffered, format=img.format)

    # Encode the resized image to Base64
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def split_image_text_types(docs):
    """
    Split base64-encoded images and texts
    """
    b64_images = []
    texts = []
    for doc in docs:
        # Check if the document is of type Document and extract page_content if so
        if isinstance(doc, Document):
            doc = doc.page_content
        if looks_like_base64(doc) and is_image_data(doc):
            doc = resize_base64_image(doc, size=(1300, 600))
            b64_images.append(doc)
        else:
            texts.append(doc)
    return {"images": b64_images, "texts": texts}


def img_prompt_func(data_dict):
    """
    Join the context into a single string
    """
    formatted_texts = "\n".join(data_dict["context"]["texts"])
    messages = []

    # Adding image(s) to the messages if present
    if data_dict["context"]["images"]:
        for image in data_dict["context"]["images"]:
            image_message = {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image}"},
            }
            messages.append(image_message)

    # Adding the text for reserachers
    text_message = {
        "type": "text",
        "text": (
            "You are an assistant tasking with providing feedback to researchers.\n"
            "You will be given a mixed of text, tables, and image(s) usually of charts or graphs.\n"
            "Use this information to provide feedback related to the user question. \n"
            f"User-provided question: {data_dict['question']}\n\n"
            "Text and / or tables:\n"
            f"{formatted_texts}"
        ),
    }
    messages.append(text_message)
    return [HumanMessage(content=messages)]


def multi_modal_rag_chain(retriever):
    """
    Multi-modal RAG chain
    """

    # Multi-modal LLM
    model = ChatOpenAI(temperature=0, model="gpt-4o-mini", max_tokens=1024)

    # RAG pipeline
    chain = (
        {
            "context": retriever | RunnableLambda(split_image_text_types),
            "question": RunnablePassthrough(),
        }
        | RunnableLambda(img_prompt_func)
        | model
        | StrOutputParser()
    )

    return chain



if __name__ == "__main__":
    # File path
    fpath = "path/to/your/pdf/directory"
    fname = "name_of_the_pdf_file.pdf"

    # Get elements
    raw_pdf_elements = extract_pdf_elements(fpath, fname)

    # Get text, tables
    texts, tables = categorize_elements(raw_pdf_elements)

    # Optional: Enforce a specific token size for texts
    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=4000, chunk_overlap=0
    )
    joined_texts = " ".join(texts)
    texts_4k_token = text_splitter.split_text(joined_texts)

    # Get text, table summaries
    text_summaries, table_summaries = generate_text_summaries(
    texts_4k_token, tables, summarize_texts=True
)

    # Image summaries
    img_base64_list, image_summaries = generate_img_summaries(fpath)

    # Add this debug print
    print(f"Number of images found: {len(img_base64_list)}")

        # The vectorstore to use to index the summaries
    vectorstore = Chroma(
        collection_name="mm_rag_js_test", embedding_function=OpenAIEmbeddings()
    )

    # Create retriever
    retriever_multi_vector_img = create_multi_vector_retriever(
        vectorstore,
        text_summaries,
        texts,
        table_summaries,
        tables,
        image_summaries,
        img_base64_list,
    )

    # Create RAG chain
    chain_multimodal_rag = multi_modal_rag_chain(retriever_multi_vector_img)

    # Check retrieval
    query = "What is the main result of the paper?"
    docs = retriever_multi_vector_img.invoke(query, limit=6)


    # We get back relevant images
    plt_img_base64(docs[0])

    #Sanity check the chain
    if len(img_base64_list) > 0:
        plt_img_base64(img_base64_list[0])
    else:
        print(f"Not enough images. Only {len(img_base64_list)} images found.")

    if len(image_summaries) > 0:
        print(image_summaries[0])
    else:
        print(f"Not enough image summaries. Only {len(image_summaries)} summaries found.")

    #RAG chain
    #response = chain_multimodal_rag.invoke({"question": query, "context": docs})
    #print(response)

    # Run RAG chain
    response = chain_multimodal_rag.invoke(query)
    print(response)
