# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import arxiv
import json
import os
import sys
from datetime import datetime, timedelta


class DailyArxivPipeline:
    def __init__(self):
        self.page_size = 100
        # delay_seconds: 增大请求间隔避免触发 arXiv API 限流 (HTTP 429)
        # num_retries: 增加重试次数以应对偶发限流
        self.client = arxiv.Client(
            page_size=self.page_size,
            delay_seconds=5.0,
            num_retries=5
        )

    def process_item(self, item: dict, spider):
        item["pdf"] = f"https://arxiv.org/pdf/{item['id']}"
        item["abs"] = f"https://arxiv.org/abs/{item['id']}"
        search = arxiv.Search(
            id_list=[item["id"]],
        )
        try:
            paper = next(self.client.results(search))
        except (arxiv.HTTPError, StopIteration) as e:
            spider.logger.warning(
                f"Failed to fetch metadata for {item['id']}: {e}. Dropping item."
            )
            return None
        item["authors"] = [a.name for a in paper.authors]
        item["title"] = paper.title
        item["categories"] = paper.categories
        item["comment"] = paper.comment
        item["summary"] = paper.summary
        return item