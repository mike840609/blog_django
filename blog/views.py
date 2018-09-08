from django.shortcuts import render , get_object_or_404
from django.http import HttpResponse
from .models import Post , Category
from comments.forms import CommentForm
import markdown

'''
def index(request):
    return HttpResponse('wellcome Mike Blog')
'''

'''
def index(request):
    return render(request , 'blog/index.html' , context={'title':'Mike Home Page ' ,  'welcome' : 'Welcome Mike Home Page' })
'''

from django.views.generic import ListView

class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

def index(request):
    post_list = Post.objects.all().order_by('-created_time')
    return render(request, 'blog/index.html', context={'post_list': post_list})

# ===============================================================================
# 直接繼承IndexView(ListView 父類別 ),省去 model , template_name
class CategoryView(IndexView):
    def get_queryset(self):
        cate = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        return super(CategoryView, self).get_queryset().filter(category=cate)


# class CategoryView(ListView):
#     model = Post
#     template_name = 'blog/index.html'
#     context_object_name = 'post_list'

#     def get_queryset(self):
#         cate = get_object_or_404(Category, pk = self.kwargs.get('pk'))
#         return super(CAtegoryView , self).get_queryset().filter(category = cate)


# def category(request , pk):
#     cate = get_object_or_404(Category , pk = pk)
#     post_list = Post.objects.filter(category = cate).order_by('-created_time')
#     return render(request,'blog/index.html',context={'post_list':post_list})

# ===============================================================================
def detail(request , pk):
    post = get_object_or_404(Post, pk = pk)

    # issue=======================================================
    # post.body = markdown.markdown(post.body, extensions = [
    #     'markdown.extensions.extra',
    #     'markdown.extensions.codehilite',
    #     'markdown.extensions.toc',
    # ] )
    # ============================================================

    # 閱讀人數  +1
    post.increase_views()


    form = CommentForm()
    comment_list = post.comment_set.all()
    context = {'post': post,
               'form': form,
               'comment_list': comment_list
               }

    return render(request , 'blog/detail.html' , context= context)

class ArchivesView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        return super(ArchivesView, self).get_queryset().filter(created_time__year=year,
                                                               created_time__month=month
                                                               )



def archives(request, year, month):
    post_list = Post.objects.filter(created_time__year=year,
                                    created_time__month=month
                                    ).order_by('-created_time')
    return render(request, 'blog/index.html', context={'post_list': post_list})
    



