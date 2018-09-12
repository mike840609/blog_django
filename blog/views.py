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

from django.views.generic import ListView , DetailView

class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    
    # 指定開啟　pagnate　功能，每一頁文章數目，自動分頁
    paginate_by = 3

    def get_context_data(self, **kwargs):
        '''
        在视图函数中将模板变量传递给模板是通过给 render 函数的 context 参数传递一个字典实现的，
        例如 render(request, 'blog/index.html', context={'post_list': post_list})，
        这里传递了一个 {'post_list': post_list} 字典给模板。
        在类视图中，这个需要传递的模板变量字典是通过 get_context_data 获得的，
        所以我们覆寫父類別方法，以便我们能够自己再插入一些我们自定义的模板变量进去。
        '''
        context = super().get_context_data(**kwargs)

        # 父類別物件取得
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')

        # 調用自己寫的　function　更新物件內容
        pagination_data = self.pagination_data(paginator , page , is_paginated)

        # 更新context　，pagination_data　也是字典
        context.update(pagination_data)

        # context 為已經更新的字典，而字典中已經有顯示分頁導航條所需的數據
        return context

    
    def pagination_data(self, paginator, page, is_paginated):
        if not is_paginated:
            return {}
        
        left_has_more = False
        right_has_more = False
        first = False
        last = False
        page_number = page.number
        total_pages = paginator.num_pages
        page_range = paginator.page_range

        left = page_range[(page_number - 3 ) if (page_number - 3 ) > 0 else 0:
                          (page_number - 1 ) if (page_number - 1 ) > 0 else 0]

        right = page_range[page_number : page_number + 2 ]

        # 若 right 串列中有值
        if right:
            if right[-1] < total_pages:
                last = True
            if right[-1] < total_pages -1 :
                right_has_more = True
        if left:
            if left[0] > 1 :
                first = True
            if left[0] > 2 : 
                left_has_more = True
        data = {
            'left' : left,
            'right' : right,
            'left_has_more' : left_has_more,
            'right_has_more' : right_has_more,
            'first' : first,
            'last':last,
        }

        return data
        


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
'''
你可以简单地把 get 方法看成是 detail 视图函数，
至于其它的像 get_object、get_context_data 都是辅助方法，
这些方法最终在 get 方法中被调用
'''
class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    
    def get(self , request , *args , **kwargs):
        # 覆写 get 方法的目的是因为每当文章被访问一次，就得将文章阅读量 +1
        # get 方法返回的是一个 HttpResponse 实例
        # 之所以需要先调用父类的 get 方法，是因为只有当 get 方法被调用后，
        # 才有 self.object 属性，其值为 Post 模型实例，即被访问的文章 post
        response = super(PostDetailView , self).get(request , *args , **kwargs)

        # 将文章阅读量 +1
        # 注意 self.object 的值就是被访问的文章 post
        self.object.increase_views()

        # get function 必須返回一個 httpResponse　物件
        return response
    
    
    def get_object(self, queryset=None):
        # 覆写 get_object 方法的目的是因为需要对 post 的 body 值进行渲染
        post = super(PostDetailView, self).get_object(queryset=None)
        # =============================
        # post.body = markdown.markdown(post.body,
        #                               extensions=[
        #                                   'markdown.extensions.extra',
        #                                   'markdown.extensions.codehilite',
        #                                   'markdown.extensions.toc',
        #                               ])
        # =============================
        return post
    
    
    def get_context_data(self , **kwargs):
        # 覆写 get_context_data 的目的是因为除了将 post 传递给模板外（DetailView 已经帮我们完成），
        # 还要把评论表单、post 下的评论列表传递给模板。
        context = super(PostDetailView , self).get_context_data(**kwargs)
        form = CommentForm()
        comment_list = self.object.comment_set.all()
        
        context.update({
            'form': form,
            'comment_list': comment_list
        })

        return context


# def detail(request , pk):

#     post = get_object_or_404(Post, pk = pk)
#     # 閱讀人數  +1
#     post.increase_views()
#     form = CommentForm()
#     comment_list = post.comment_set.all()
#     context = {'post': post,
#                'form': form,
#                'comment_list': comment_list
#                }
#     return render(request , 'blog/detail.html' , context= context)

# ===============================================================================
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
    



