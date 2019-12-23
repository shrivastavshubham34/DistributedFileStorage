#!/usr/bin/env python
# -*- coding: utf-8
from tree_node import TreeNode
from sortedcontainers import SortedDict
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

#tracking number of free pages globals
DEBUG = 0
ADD = "add"
REMOVE = "remove"
PRINT_LIST_BREAK = 5


class SpaceBinaryTree:
    '''
    Atrributes
    '''
    free_pages = 0
    sorted_dict = None

    '''
    Methods
    '''

    # Constructor
    def __init__(self, free_pages):
        #keep track of the number of pages free
        self.free_pages = free_pages
        # define the attributes
        #creating the list of indexes to keep track.
        free_pages_available = [x for x in range(free_pages)]
        # self.head = TreeNode(node_left=None, node_right=None, size=size, free_pages=free_pages)
        self.sorted_dict = SortedDict({free_pages: TreeNode(free_pages=[free_pages_available])})

    def set_empty_space(self, num_of_slots, free_pages):
        if DEBUG:
            logger.debug("[space_binary_tree] Inside set empty_space")
            logger.debug("[space_binary_tree] About to set the num_of_free_pages")
            logger.debug("[space_binary_tree] number of slots to free: {}".format(num_of_slots))
            logger.debug("[space_binary_tree] free pages: {}".format(self.free_pages))

        self.set_num_free_pages(ADD, num_of_slots)

        if DEBUG:
            logger.debug("[space_binary_tree] Already set the num_of_free_pages")
            logger.debug("[space_binary_tree] number of slots to free: {}".format(num_of_slots))
            logger.debug("[space_binary_tree] free pages: {}".format(self.free_pages))


        if self.sorted_dict.get(num_of_slots):
            if DEBUG:
                logger.debug("[space_binary_tree] Number of slots exist in sorted_dict")
                # logger.debug("[space_binary_tree] free pages given: {}".format(free_pages))
                logger.debug("[space_binary_tree] sorted_dict: {}".format(self.sorted_dict.get(num_of_slots).size))
                self.sorted_dict.get(num_of_slots).print_free_pages()

            self.sorted_dict.get(num_of_slots).set_free_pages(free_pages)

        # If the key does not exist, then we create a new node and add
        # the list to a new node
        else:
            if DEBUG:
                logger.debug("[space_binary_tree] New entry")
                logger.debug("[space_binary_tree] free pages given:")

            self.sorted_dict[num_of_slots] = TreeNode(size=num_of_slots,
                                                      free_pages=[free_pages])

    # else:
    # print("Index Error, the node has no list remaining")

    def set_num_free_pages(self, mode, value):
        if mode == ADD:
            self.free_pages += value
        elif mode == REMOVE:
            self.free_pages -= value
        else:
            raise

    def get_total_free_pages(self):
        return self.free_pages



    def get_available_space(self, number_of_chunks):
        #number of spaces is available in sorted dict
        '''
        :param number_of_chunks:
        :return:
        '''

        '''
        The data structure can find the exact number of pages requested
        if it does find a spot that fits, it can allocate that space
        '''
        if DEBUG:
            print("[SpaceBinaryTree] Number of chunks needed = {}".format(number_of_chunks))
            print("[SpaceBinaryTree] doe sit exist? = {}".format(self.sorted_dict.get(number_of_chunks)))

        #print("[SpaceBinaryTree] resultado del if = {}".format(self.sorted_dict.get(number_of_chunks)))
        if self.sorted_dict.get(number_of_chunks):
            if DEBUG:
                print("[SpaceBinaryTree] inside if number of chunks matches available")

            temp_node = self.sorted_dict.pop(number_of_chunks)
            ret_list = temp_node.get_free_pages()
            self.set_num_free_pages(REMOVE, number_of_chunks)

            if not temp_node.is_node_empty():
                self.sorted_dict[number_of_chunks] = temp_node

            # ret_list = self.sorted_dict.get(number_of_chunks).get_free_pages()


            if DEBUG:
                for i, index in enumerate(ret_list):
                    print("[SpaceBinaryTree] return list item: {}".format(ret_list[i]))
                    if i >= PRINT_LIST_BREAK:
                        break

            return ret_list
        else:
            '''
            Either the chunck is largest or smallest than the chunks available.
            '''
            try:
                #print("[SpaceBinaryTree] chunks needed are not found in list, has to be built")
                # Get the largest space available from sorted dict
                largest_chuck = self.sorted_dict.keys()[-1]
                if DEBUG:
                    print("[SpaceBinaryTree] number of chunks needed is not available in the data structure")
                    print("[SpaceBinaryTree] we need to create a list of free pages")
                    print("[SpaceBinaryTree] Largest chunk available: {}".format(largest_chuck))

                #print("[SpaceBinaryTree] largest chunk is = {}".format(largest_chuck))
                # Find if the number of chunks needed is lower than the largest available
                if number_of_chunks < largest_chuck:
                    if DEBUG:
                        print("[SpaceBinaryTree] number of chunks: {}".format(number_of_chunks))
                        print("[SpaceBinaryTree] largest chunk available in data structure: {}".format(largest_chuck))
                        print("[SpaceBinaryTree] Largest chunk is bigger than number of chunks needed")
                    # if it is, we need to take one of those chunks and break it down
                    #first we get the whole node out of the sorted dict
                    if DEBUG:
                        print("[SpaceBinaryTree] Getting the largest chunk node into a temp location")
                    temp_node = self.sorted_dict.pop(largest_chuck)
                    self.set_num_free_pages(REMOVE, largest_chuck)
                    #print("[SpaceBinaryTree] Temp node popped out of list = {}".format(temp_node.get_size()))
                    #find if the node free pages list is not empty
                    #print("[SpaceBinaryTree] Temp node is empty = {}".format(temp_node.is_node_empty()))
                    if not temp_node.is_node_empty():
                        if DEBUG:
                            print("[SpaceBinaryTree] Node is not empty")
                        # pop the first list of pages available in the free_pages list.
                        # remember that free pages is a list if list of pages
                        # The structure is to be able to keep list of pages that are the same size under
                        # a single dictionary with key number of free pages
                        #print("[spaceBinaryTree] inside the not empty node")
                        # temp_node.print_free_pages()
                        temp_list = temp_node.get_free_pages()
                        if DEBUG:
                            if isinstance(temp_list, list):
                                for i, index in enumerate(temp_list):
                                    print("[SpaceBinaryTree] return list from free_pages: {}".format(temp_list[i]))
                                    if i >= PRINT_LIST_BREAK:
                                        break
                            else:
                                print("[SpaceBinaryTree] Temp list is not a list!!!!!!!!")
                                print("[SpaceBinaryTree] Temp list is = {}".format(temp_list))
                        # Once we have the new list, we need to split it into the pages
                        # needed nad the remaining ones.
                        ret_list = temp_list[:number_of_chunks]
                        if DEBUG:
                            for i, index in enumerate(ret_list):
                                print("[SpaceBinaryTree] return list item: {}".format(ret_list[i]))
                                if i >= PRINT_LIST_BREAK:
                                    break
                        #keep track of the total number of pages available
                        # self.set_num_free_pages(REMOVE, number_of_chunks)
                        if DEBUG:
                            print("[SpaceBinaryTree] removing the number of spaces from the number of available spaces")
                            print("[SpaceBinaryTree] calling set_free_pages with {}: {}".format(REMOVE, number_of_chunks))
                        #print("Return list found = {}".format(len(ret_list)))
                        # Then we store the remaining list in an existing key
                        rem_list = temp_list[number_of_chunks:]
                        if DEBUG:
                            for i, index in enumerate(rem_list):
                                print("[SpaceBinaryTree] remaining list item: {}".format(rem_list[i]))
                                if i >= PRINT_LIST_BREAK:
                                    break
                        #print("Remaining list left = {}".format(len(rem_list)))
                        self.set_empty_space(len(rem_list), rem_list)
                        if DEBUG:
                            for i, index in enumerate(rem_list):
                                print("[SpaceBinaryTree] remaining list set space: {}".format(rem_list[i]))
                                if i >= PRINT_LIST_BREAK:
                                    break
                            print("[SpaceBinaryTree] setting empty space with length {}".format(len(rem_list)))
                        return ret_list
                    else:
                        err_message = "You got an empty node"
                        raise Exception(err_message)
                else:
                    if DEBUG:
                        print("[SpaceBinaryTree] number of chunks: {}".format(number_of_chunks))
                        print("[SpaceBinaryTree] largest chunk available in data structure: {}".format(largest_chuck))
                        print("[SpaceBinaryTree] Largest chunk is smaller than number of chunks needed")
                    # Get the smallest space available from sorted dict
                    smallest_chuck = self.sorted_dict.keys()[0]
                    # Take smallest pieces and get as many until enough chunks
                    # meet the chunks needed
                    temp_node = self.sorted_dict.pop(smallest_chuck)
                    #number of chunks is larger than largest spot available.
                    enough_pages = False
                    ret_list = []
                    free_pages_needed = number_of_chunks
                    ret_list = None
                    # We are going to start looking at the smallest set of page lists
                    # and we are going to add as many pages needed for the chunks to fit in
                    while not enough_pages:
                        # The list of pages is smaller than needed at this point
                        if free_pages_needed[0] > smallest_chuck:
                        # Cycle through all the pages in the node and try to fill the gap
                            for lp in self.sorted_dict.get(smallest_chuck).get_all_free_pages():
                                if free_pages_needed > len(lp):
                                    ret_list = ret_list + lp
                                    free_pages_needed = free_pages_needed - len(ret_list)

                                else:
                                    ret_list = ret_list + lp[:free_pages_needed]
                                    free_pages_left = free_pages_needed - len(ret_list)
                                    #if there are any pages left after the split
                                    if free_pages_left > 0:
                                        self.set_empty_space(len(free_pages_needed), lp[free_pages_needed:])

                                    enough_pages = True

                                if enough_pages == True:
                                    self.sorted_dict.pop[0]
                                    self.set_num_free_pages(REMOVE,number_of_chunks)
                                    return ret_list
                                else:
                                    self.sorted_dict.pop(0)
                                    continue

            except Exception as e:
                print(str(e))
                raise






