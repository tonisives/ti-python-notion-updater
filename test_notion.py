from unittest import TestCase

from notion import Notion

"""
Tests against a live Notion page. define "api_key, and page/block ids for each of the tests.
"""


class TestNotion(TestCase):
    ## DONT COMMIT
    api_key = "secret_YOUR_SECRET"
    ## DONT COMMIT

    # block with text "30 minutes ago"
    page_id = "778d046c-26fa-4600-b736-959892fe9d46"
    block_with_30_minutes_text_id = "cfdd7710-2626-42cd-9a4a-cfb685d19f89"
    # just a text block. image will be appended as a child here
    block_to_append_image = "99984818-106d-43a9-aca2-3980e2bf3cb2"
    notion = Notion(api_key)

    def test_search_page(self):
        pages = self.notion.search_page()
        assert len(pages) > 0

    def test_get_page(self):
        page = self.notion.get_page(self.page_id)
        assert page["id"] == self.page_id

    def test_get_block(self):
        block = self.notion.get_block(self.page_id)
        assert block["id"] == self.page_id
        pass

    def test_get_block_children(self):
        children = self.notion.get_block_children(self.page_id)
        assert len(children) > 1

    def test_update_block(self):
        # define a block with text "30 minutes ago".
        # test will change it to "31 minutes ago" and then back to "30"

        block = self.notion.get_block(self.block_with_30_minutes_text_id)
        assert block["paragraph"]["text"][0]["text"]["content"] == "30 minutes ago"

        block["paragraph"]["text"][0]["text"]["content"] = "31 minutes ago"
        updated_block = self.notion.update_block(self.block_with_30_minutes_text_id, block)

        assert updated_block["paragraph"]["text"][0]["text"]["content"] == "31 minutes ago"

        # cleanup
        block["paragraph"]["text"][0]["text"]["content"] = "30 minutes ago"
        self.notion.update_block(self.block_with_30_minutes_text_id, block)
        pass

    def test_append_and_delete_block(self):
        block = self.notion.get_block(self.block_with_30_minutes_text_id)
        assert block["has_children"] == False
        # append a copy of the block
        result = self.notion.append_child_blocks(self.block_with_30_minutes_text_id, [block])
        assert result["has_children"] == True

        # delete
        children = self.notion.get_block_children(self.block_with_30_minutes_text_id)
        self.notion.delete_block(children[0]["id"])

    def test_update_block_text(self):
        response = self.notion.text_set(self.block_with_30_minutes_text_id, "test")
        assert self.notion.text_get(response) == "test"
        ## cleanup
        self.notion.text_set(self.block_with_30_minutes_text_id, "30 minutes ago")

    def test_update_image_block(self):
        # block = self.notion.get_block(self.block_with_image)
        block = self.notion.get_block(self.block_to_append_image)
        assert block["has_children"] == False

        result = self.notion.image_add(self.block_to_append_image,
                                       "https://cdn-icons-png.flaticon.com/512/1753/1753962.png")
        assert result["has_children"] == True

        # delete
        children = self.notion.get_block_children(self.block_to_append_image)
        self.notion.delete_block(children[0]["id"])
