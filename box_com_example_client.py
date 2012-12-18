#!/usr/bin/env python
# -*- coding: utf-8 -*-

import box_lib as box

API_KEY = "__ADD_YOUR_API_KEY_HERE__"

# auth user
auth = box.BoxNetAuth()
auth.set_api_key(API_KEY)
auth.auth_user_part1()

raw_input("Press Return after registration!")
auth.auth_user_part2()

# create client
client = box.BoxNetClient(API_KEY)

# upload file
client.upload_file("/the/path/to/your/file")

# delete a file
client.delete_file("__id_of_file__")

# search
client.search_content("a file name")


