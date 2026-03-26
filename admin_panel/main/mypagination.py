from rest_framework.pagination import PageNumberPagination

class mypaginatior(PageNumberPagination):
    page_size = 2
    page_query_param = 'p'
    page_size_query_param = 'records'
    max_page_size = 4
    last_page_strings = ['end'] 


# ---------- Limite Offset ------------------
# from rest_framework.pagination import LimitOffsetPagination

# class mypaginatior(LimitOffsetPagination):
#     default_limit = 2
#     limit_query_param = 'mylimit'
#     offset_query_param = 'myoffset'
#     max_limit = 4

# ---------- Cursor Pagination --------------

# from rest_framework.pagination import CursorPagination

# class mypaginatior(CursorPagination):
#     page_size = 2   
#     ordering = '-id'
#     cursor_query_param = 'cu' 
