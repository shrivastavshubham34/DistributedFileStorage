#!/usr/bin/env python
# -*- coding: utf-8
import math
import time
import os
import sys
import logging

from page import Page
from space_binary_tree import SpaceBinaryTree

sys.path.append("../" + os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/utils/')
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/generated/')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

DEBUG = 0
ADD = "add"
REMOVE = "remove"
PRINT_LIST_BREAK = 5

class MemoryManager:
    '''
    Atrributes
    '''

    memory_tracker = None  # key: memory_hash_id, value: list_of_pages_ids>
    list_of_all_pages = []
    total_number_of_pages = 0
    total_memory_size = 0
    page_size = 0
    list_of_pages_used = []
    fragmentation_threshold = 0
    pages_free = None

    '''
    Methods
    '''
    # Constructor
    def __init__(self, total_memory_size, page_size):

        # define the attributes
        self.total_memory_size = total_memory_size
        self.page_size = page_size
        self.memory_tracker = {}

        self.total_number_of_pages = math.floor(self.total_memory_size / self.page_size)

        for i in range(self.total_number_of_pages):
            self.list_of_all_pages.append(Page(self.page_size))

        self.pages_free = SpaceBinaryTree(self.total_number_of_pages)
        logger.debug("Number of pages available in memory %s of size %s bytes." % (len(self.list_of_all_pages),
                                                                                           self.page_size))

    # def put_data(self, memory_id, data_chunks, num_of_chunks):
    def put_data(self, data_chunks, hash_id, chunk_size, number_of_chunks, is_single_chunk):

        '''
        :param data_chunks:
        :param hash_id:
        :param chunk_size:
        :param data_size:
        :return:
        '''

        # if the incoming chunk size is bigger than the page sie
        chunks_to_split_multiplier = math.ceil(chunk_size / self.page_size)
        pages_needed = number_of_chunks * chunks_to_split_multiplier

        if hash_id in self.memory_tracker:
            logger.debug("The following hash_id exist and it will be overwritten: %s." % hash_id)
            # delete data associated this this hash_id before we save the new one
            self.delete_data(hash_id)
        else:
            logger.debug("Writing new data with hash_id: %s." % hash_id)


        if DEBUG:
            logger.debug("[memory manager] start time for getting pages")
            start_find_pages_time = time.time()

        # find available blocks of pages to save the data
        target_list_indexes = self.find_n_available_pages(pages_needed)
        start_write_data = time.time()

        # save the data in pages
        index_counter = 0
        if not is_single_chunk:
            for c in data_chunks:
                if chunks_to_split_multiplier > 1:
                    for p in range(0, chunks_to_split_multiplier):
                        #print(p*self.page_size, ":",  (p+1)*self.page_size)
                        self.list_of_all_pages[target_list_indexes[index_counter]].put_data(c.chunk[p*self.page_size: (p+1)*self.page_size])
                        index_counter = index_counter + 1
                else:
                    self.list_of_all_pages[target_list_indexes[index_counter]].put_data(c.chunk)
                    index_counter = index_counter + 1

        else:
            self.list_of_all_pages[target_list_indexes[index_counter]].put_data(data_chunks.chunk)
            index_counter = index_counter + 1

        total_time_write_data = round(time.time() - start_write_data, 6)

        assert index_counter == pages_needed  # make sure we use all the pages we needed

        # update memory dic
        self.memory_tracker[hash_id] = target_list_indexes

        logger.debug("Successfully saved the data in %s pages. Bytes written: %s. Took %s seconds." %
              (pages_needed, pages_needed * self.page_size, total_time_write_data))
        logger.debug("Free pages left: %s. Bytes left: %s" % (self.get_number_of_pages_available(), self.get_available_memory_bytes()))

        return True

    def get_number_of_pages_available(self):
        return self.pages_free.get_total_free_pages()

    def get_available_memory_bytes(self):
        return self.get_number_of_pages_available() * self.page_size

    def get_data(self, hash_id):
        '''
        :param hash_id:
        :return:
        '''

        pages_to_return = []

        if hash_id not in self.memory_tracker:
            logger.debug("Hash id not found. Returning empty data for hash_id", hash_id)
            return pages_to_return

        data_pages = self.memory_tracker[hash_id]
        start_read_data = time.time()

        for index in data_pages:
            pages_to_return.append(self.list_of_all_pages[index].get_data())

        total_time_read_data = round(time.time() - start_read_data, 6)

        logger.debug("Returning: data for %s composed of %s pages. Took %s sec" %
              (hash_id, str(len(pages_to_return)), total_time_read_data))

        return pages_to_return

    def update_data(self, data, memory_id):
        '''
        :param data:
        :param memory_id:
        :return:
        '''
        # TODO
        pass

    # this function is very slow, we need to improve it. (This will use a tree)
    def find_n_available_pages(self, n):

        start = time.time()
        logger.debug("Looking for %s available pages... " % n)
        message = ("Not enough pages available to save the data. Pages needed: {}, pages available {}. Available bytes: {}"
                   .format(n, self.get_number_of_pages_available(), self.get_available_memory_bytes()))
        if n > self.get_number_of_pages_available():
            logger.debug(message)

        list_indexes_to_used = self.pages_free.get_available_space(n)
        total_time = round(time.time() - start, 6)

        if len(list_indexes_to_used) != n:
            logger.debug("Not enough pages available to save the data. Took %s seconds." % total_time)
        else:
            logger.debug("Enough pages available to save the data. Took %s seconds." % total_time)

        return list_indexes_to_used

    def delete_data(self, hash_id):
        '''
        :param hash_id:
        :return:
        '''
        # find the data from the memory storage
        if DEBUG:
            logger.debug("[memory manager] Entering the delete data function")
        #get the list of pages used
        old_pages_list = self.memory_tracker.pop(hash_id)
        if DEBUG:
            logger.debug("[memory manager] len of list to remove: {}".format(len(old_pages_list)))

        #add pages to the free pages structure
        self.pages_free.set_empty_space(len(old_pages_list),old_pages_list)

        if DEBUG:
            logger.debug("[memory manager] called set_empty_space | num_of slots: {}".format(len(old_pages_list)))
        #delete the memory tracker
        # del self.memory_tracker[hash_id]  # delete the mapping
        # self.list_of_pages_used = [x for x in self.list_of_pages_used if x not in old_pages_list]
        # we may also need to delete the data from the actual Pages() in list_of_all_pages
        logger.debug("Successfully deleted hash_id: %s." % hash_id)

    def get_stored_hashes_list(self):
        return list(self.memory_tracker.keys())

    def hash_id_exists(self, hash_id):
        if hash_id in self.memory_tracker:
            return True
        else:
            return False

    def defragment_data(self):
        '''
        :param data:
        :param list_of_pages:
        :return:
        '''
        # TODO
        pass

    def partition_data(self, data, list_of_pages):
        '''
        :param data:
        :param list_of_pages:
        :return:
        '''
        # TODO
        pass

    def update_binary_tree(self):
        '''
        :return:
        '''
        # TODO
        pass
