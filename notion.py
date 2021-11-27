import json

import requests

"""
All requests return either a json object or dict with "error" and "code" values
"""


class Notion:

    def __init__(self, notion_token):
        self.headers = {
            'Notion-Version': '2021-05-13',
            'Authorization': 'Bearer ' + notion_token,
            "Content-Type": "application/json"
        }
        self.base_url = "https://api.notion.com/v1"

    def search_page(self, page_title: str = None):
        """
        Search for a page
        :param page_title: The page title
        :return: List of pages
        """
        url = self.base_url + "/search"
        body = {}
        if page_title is not None:
            body["query"] = page_title

        response = requests.request("POST", url, headers=self.headers, params=body)
        return self.response_or_error(response)

    def get_page(self, page_id: str):
        url = self.base_url + f"/pages/{page_id}"
        response = requests.request("GET", url, headers=self.headers)
        return self.response_or_error(response)

    def get_page_children(self, page_id: str):
        """
        Get page children
        https://developers.notion.com/reference/get-block-children
        :return: Page dict
        """
        return self.get_block_children(page_id)

    def get_block(self, block_id: str):
        """
        Get a Notion block
        https://developers.notion.com/reference/retrieve-a-block
        :return: Block dict
        """
        url = self.base_url + f"/blocks/{block_id}"
        response = requests.request("GET", url, headers=self.headers)
        return self.response_or_error(response)

    def get_block_children(self, block_id: str):
        """
        Get block children
        https://developers.notion.com/reference/get-block-children
        :return: List of children
        """

        # get https://api.notion.com/v1/blocks/block_id/children
        url = self.base_url + f"/blocks/{block_id}/children"
        response = requests.request("GET", url, headers=self.headers)
        return self.response_or_error(response, "results")

    def update_block(self, block_id: str, content: dict):
        """
        Update a block
        https://developers.notion.com/reference/update-a-block
        :return: Updated block
        """
        url = self.base_url + f"/blocks/{block_id}"
        # content = json.dumps(content)
        response = requests.request("PATCH", url, headers=self.headers, json=content)
        return self.response_or_error(response)

    def append_child_blocks(self, parent_id: str, children: []):
        """
        Append a block
        https://developers.notion.com/reference/patch-block-children
        :param parent_id: The parent block where children are added
        :param children: Array of blocks to be added
        :return: Appended blocks
        """
        url = self.base_url + f"/blocks/{parent_id}/children"
        response = requests.request(
            "PATCH",
            url,
            headers=self.headers,
            json={"children": children}
        )
        return self.response_or_error(response)

    def delete_block(self, block_id: str):
        """
        Delete a block
        https://developers.notion.com/reference/delete-a-block
        :return: Updated block
        """
        url = self.base_url + f"/blocks/{block_id}"
        response = requests.request("DELETE", url, headers=self.headers)
        return self.response_or_error(response)

    # def update_database(self):
    #     """
    #     Update a database
    #     https://developers.notion.com/reference/update-a-database
    #     :return:
    #     """
    #     # patch https://api.notion.com/v1/databases/database_id
    #     pass

    # MARK: block update helpers

    text_block_types = ["paragraph", "heading_1", "heading_2", "heading_3"]

    def text_append(self, parent_id: str, text: str):
        """
        Append text block as a child to parent.
        :param block_id: The block to which the text will be appended
        :param text: The text
        :return: The new block
        """

        text_block = {
            "type": "paragraph",
            "paragraph": {
                "text": [{
                    "type": "text",
                    "text": {
                        "content": text,
                    }
                }]
            }
        }
        return self.append_child_blocks(parent_id, [text_block])

    def text_set(self, block_id: str, new_text: str):
        """
        Updates a block text. block["type"] must be one from the "text_block_types"

        :param block_id: The block id with text
        :param new_text: New text set for the block
        :return: The new block
        """
        block = self.get_block(block_id)
        type = block["type"]

        if type not in self.text_block_types:
            return {"code": 0, "error": "Not a text block"}

        block[type]["text"][0]["text"]["content"] = new_text
        return self.update_block(block_id, block)

    def text_get(self, block: dict):
        """
        Gets a block text.
        :param block: block dict
        :return: block text str
        """
        type = block["type"]

        if type not in self.text_block_types:
            return None

        return block[type]["text"][0]["text"]["content"]

    def image_add(self, parent_id: str, image_url: str):
        """
        Adds an image block as a child to a parent.
        Currently cannot update the image: https://developers.notion.com/reference/update-a-block,
        so need to manually delete the old image block and add a new one.

        :param parent_id: The parent block id
        :param image_url: The image url
        :return: The parent block
        """
        append_children = [
            {
                "type": "image",
                "image": {
                    "type": "external",
                    "external": {
                        "url": image_url
                    }
                }
            }
        ]

        return self.append_child_blocks(parent_id, append_children)

    def image_get_url(self, block: dict):
        type = block["type"]

        if type != "image":
            return None

        return block["image"]["external"]["url"]

    @staticmethod
    def response_or_error(response, key: str = None):
        response_json = response.json()

        if "message" in response_json:
            message = response_json["message"]
            return {
                "code": response.status_code,
                "error": message
            }

        json_response = response.json()

        if key is not None:
            return json_response[key]

        return json_response
