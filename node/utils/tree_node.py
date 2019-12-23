#!/usr/bin/env python
# -*- coding: utf-8
import logging

DEBUG = 0
PRINT_LIST_BREAK = 5

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class TreeNode:
    node_left = None
    node_right= None
    size = 0
    free_pages = []

    def __init__(self, size=0, free_pages=[]):
        self.size = size
        self.free_pages = free_pages

    def set_size(self, size):
        self.size = size

    def set_free_pages(self, pages):
        self.free_pages.append(pages)

    def get_size(self):
        return self.size;

    def get_all_free_pages(self):
        return self.free_pages

    def get_free_pages(self):
        if DEBUG:
            logger.debug("[Tree Node] inside get_free_pages")
            logger.debug("[Tree Node] lenght of the firts value of free pages: {}". format(len(self.free_pages)))
            if len(self.free_pages[0]) < 5:
                logger.debug("[Tree Node] content of free pages first element{}".format(self.free_pages))

        if self.is_node_empty():
            return []
        else:
            ret_val = self.free_pages.pop()
            if DEBUG:
                if isinstance(ret_val, list):
                    for i, index in enumerate(ret_val):
                        if isinstance(ret_val[i], list):
                            print("[memory manager] this should not be a list")
                            print("[memory manager] first element is : {}".format(ret_val[i][0]))
                            break
                        logger.debug("[Tree Node] return object : {}".format(ret_val[i]))
                        if i >= PRINT_LIST_BREAK:
                            break
                else:
                    logger.debug("[Tree Node] return value is not a list!!!!!!!!")
                    logger.debug("[Tree Node] return value is = {}".format(ret_val))
            return ret_val


    def is_node_empty(self):
        if self.free_pages == []:
            return True
        else:
            return False

    def print_free_pages(self):
        max_numbers = 5
        for i, set_of_pages in enumerate(self.free_pages):
            if isinstance(set_of_pages, list):
                temp_list = []
                for j, element in enumerate(set_of_pages):
                    temp_list.append(element)
                    if j > max_numbers:
                        break
                print("[TreeNode] list {}: {}".format(i, temp_list))
