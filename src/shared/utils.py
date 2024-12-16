"""Shared utility functions used in the project.

Functions:
    format_docs: Convert documents to an xml-formatted string.
    load_chat_model: Load a chat model from a model name.
"""
import logging
import os
from typing import Optional

from langchain.chat_models import init_chat_model
from langchain_core.documents import Document
from langchain_core.language_models import BaseChatModel

logger = logging.getLogger(__name__)


def _format_doc(doc: Document) -> str:
    """Format a single document as XML.

    Args:
        doc (Document): The document to format.

    Returns:
        str: The formatted document as an XML string.
    """
    metadata = doc.metadata or {}
    meta = "".join(f" {k}={v!r}" for k, v in metadata.items())
    if meta:
        meta = f" {meta}"

    return f"<document{meta}>\n{doc.page_content}\n</document>"


def format_docs(docs: Optional[list[Document]]) -> str:
    """Format a list of documents as XML.

    This function takes a list of Document objects and formats them into a single XML string.

    Args:
        docs (Optional[list[Document]]): A list of Document objects to format, or None.

    Returns:
        str: A string containing the formatted documents in XML format.

    Examples:
        >>> docs = [Document(page_content="Hello"), Document(page_content="World")]
        >>> print(format_docs(docs))
        <documents>
        <document>
        Hello
        </document>
        <document>
        World
        </document>
        </documents>

        >>> print(format_docs(None))
        <documents></documents>
    """
    if not docs:
        return "<documents></documents>"
    formatted = "\n".join(_format_doc(doc) for doc in docs)
    return f"""<documents>
{formatted}
</documents>"""


def load_chat_model(fully_specified_name: str, response_model_kwargs: Optional[dict] = None) -> BaseChatModel:
    """Load a chat model from a fully specified name.

    Args:
        fully_specified_name (str): String in the format 'provider/model'.

    Returns:
        BaseChatModel: An instance of the loaded chat model.
        :param fully_specified_name:
        :param response_model_kwargs:
    """
    http_client, http_async_client = _get_proxy_clients()

    # Parse the provider and model from the name
    if "/" in fully_specified_name:
        provider, model = fully_specified_name.split("/", maxsplit=1)
    else:
        provider = ""
        model = fully_specified_name

    if provider == "gigachat":
        from langchain_community.chat_models.gigachat import GigaChat
        return GigaChat(verify_ssl_certs=False, scope="GIGACHAT_API_PERS", temperature=0)

    if provider == "xai":
        from langchain_xai import ChatXAI
        return ChatXAI(model=model, temperature=0, http_async_client=http_async_client)

    # Prepare common parameters for initializing the model
    base_url = os.getenv("PROXY_LLM_API_BASE_URL")
    api_key = os.getenv("PROXY_LLM_API_KEY")
    base_common_params = {
        "model": model,
        "model_provider": provider,
    }
    if not response_model_kwargs:
        response_model_kwargs = {
            "temperature": 0
        }

    common_params = {**base_common_params, **response_model_kwargs}
    if provider.lower() == "ollama":
        # Initialize the ChatOllama model with the correct base_url
        common_params["base_url"] = os.getenv("OLLAMA_BASE_URL")

    # Use asynchronous client if available
    if http_async_client:
        common_params["http_async_client"] = http_async_client
    else:
        common_params["http_client"] = http_client

    # Include API key and base URL if available
    if base_url and api_key:
        common_params.update({"api_key": api_key, "base_url": base_url})

    # Initialize and return the chat model
    return init_chat_model(**common_params)


def _get_proxy_clients():
    """
    Creates synchronous and asynchronous HTTP clients, with optional proxy configuration.
    :return: A tuple of (http_client, http_async_client) where either or both could be None if no proxy is provided.
    """
    # Initialize variables for HTTP client and async client, defaults to None
    import httpx
    import os
    from urllib.parse import urlparse

    http_client = None
    http_async_client = None

    proxy_url = os.environ.get("PROXY_URL")

    # Check if proxy URL is provided and valid
    if proxy_url:
        parsed_url = urlparse(proxy_url)
        if parsed_url.scheme and parsed_url.netloc:
            http_client = httpx.Client(proxies=proxy_url)
            http_async_client = httpx.AsyncClient(proxies=proxy_url)
        else:
            logger.warn("Invalid proxy URL provided. Proceeding without proxy.")

    return http_client, http_async_client


def create_service_with_proxy(service_class, model, **kwargs):
    """
    Creates an instance of a given service class, injecting proxy-aware HTTP clients if available.

    :param service_class: The service class you want to instantiate (e.g., OpenAIEmbeddings).
    :param model: An object that contains model name.
    :param kwargs: Additional keyword arguments to pass to the service class.
    :return: An instance of the service class.
    """
    # Get proxy clients
    http_client, http_async_client = _get_proxy_clients()

    # Inject HTTP client into the kwargs if a valid one exists
    if http_client:
        kwargs['http_client'] = http_client
    if http_async_client:
        kwargs['http_async_client'] = http_async_client

    base_url = os.getenv("PROXY_LLM_API_BASE_URL")
    api_key = os.getenv("PROXY_LLM_API_KEY")

    # Include API key and base URL if available
    if base_url and api_key:
        kwargs['base_url'] = base_url
        kwargs['api_key'] = api_key

    # Create and return the service class instance with all necessary arguments
    return service_class(
        model=model,
        **kwargs
    )
