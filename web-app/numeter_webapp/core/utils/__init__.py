from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def make_page(List, pagenum, num):
    paginator = Paginator(List, num)
    try:
        page = paginator.page(pagenum)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    return page
