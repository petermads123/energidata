"""Generic API class for different APIs."""

import io
import json
import zipfile

import requests
import xmltodict

from energidata.utils.wrappers import retry


class GenericAPI:
    """Generic API class."""

    def __init__(self) -> None:
        """Initialize the GenericAPI class."""

    @retry()
    def call(
        self, url: str, params: dict | None = None, headers: dict | None = None
    ) -> dict:
        """Call the API with given URL, parameters, and headers.

        Args:
            url (str): The API endpoint URL.
            params (dict | None, optional): The parameters for the API call. Default is None.
            headers (dict | None, optional): The headers for the API call. Default is None.

        Returns:
            dict: The JSON response from the API.
        """
        # Call the API
        response = requests.get(url, params=params, headers=headers)
        # Check for errors (this will trigger the retry mechanism)
        response.raise_for_status()

        # Parse the response content
        result = self._parse_response_to_dict(response)

        return result

    def _parse_response_to_dict(self, response: requests.Response) -> dict:
        """Parses an HTTP response and returns its contents as a Python dictionary.

        Handles JSON, XML, ZIP (with JSON/XML), and multiple files in ZIP.

        Args:
            response (requests.Response): The HTTP response object to parse.

        Returns:
            dict: The parsed content as a Python dictionary.
        """
        content_type = response.headers.get("Content-Type", "").lower()

        # Handle JSON content directly
        if "application/json" in content_type:
            return response.json()

        # Handle XML content directly
        if "application/xml" in content_type or "text/xml" in content_type:
            return xmltodict.parse(response.text)

        # Handle ZIP content
        if (
            "application/zip" in content_type
            or "application/octet-stream" in content_type
        ):
            return self._parse_zip_content(response.content)

        # Fallback: try parsing as JSON or XML
        try:
            return response.json()
        except ValueError:
            try:
                return xmltodict.parse(response.text)
            except Exception as exc:
                raise ValueError(
                    "Unknown content format, unable to parse as JSON, XML, or ZIP"
                ) from exc

    def _parse_zip_content(self, content: bytes) -> dict:
        """Extracts and parses files inside a ZIP archive blob.

        Returns a dict with filenames as keys and parsed file contents as values.
        Supports multiple JSON and XML files in the archive.

        Args:
            content (bytes): The binary content of the ZIP archive.

        Returns:
            dict: A dictionary with filenames as keys and parsed contents as values.
        """
        file_dict = {}
        with zipfile.ZipFile(io.BytesIO(content)) as zipped_file:
            for filename in zipped_file.namelist():
                with zipped_file.open(filename) as f:
                    file_content = f.read()
                    if filename.endswith(".json"):
                        file_dict[filename] = json.loads(file_content.decode("utf-8"))
                    elif filename.endswith(".xml"):
                        file_dict[filename] = xmltodict.parse(
                            file_content.decode("utf-8")
                        )
                    else:
                        file_dict[filename] = file_content  # raw bytes for non-JSON/XML
        return file_dict
