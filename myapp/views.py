from django.shortcuts import render
from django.http import HttpResponse, request
from myapp.models import *
from django.forms.models import model_to_dict

def search_list(request):
    if 'cname' in request.GET:
        cname = request.GET['cname']
        print(f'cname: {cname}')
        resultList = students.objects.filter(cname__icontains=cname).order_by('-cid')
    else:
        # orm語法，目的：取得所有學生資料，並依照cid排序
        resultList = students.objects.all().order_by('-cid')
        for student in resultList:
            print(model_to_dict(student))

    #resultList = [] # 測式若無資料時，清空列表
    errormessage = ""
    if not resultList:
        errormessage = "查無資料."
    
    # return HttpResponse("This is the search list view.")
    # return render(request, 'search_list.html', {'resultList': resultList})
    return render(request, 'search_list.html', locals())

def search_name(request):
    return render(request, 'search_name.html')

def index(request):
    if 'site_search' in request.GET:
        site_search = request.GET['site_search']
        site_search = site_search.strip() # 去除前後空白
        # print(f"site_search: {site_search}")
        # 切割關鍵字，依空白分隔
        keywords = site_search.split() 
        print(f"keywords: {keywords}")
        # by github copilot
        # 多個關鍵字搜尋，搜尋cname, cbirthday, cemail, cphone, caddr
        from django.db.models import Q
        query = Q()
        for keyword in keywords: # query |=相似 i = i+1
            query |= (
                Q(cname__icontains=keyword) |
                Q(cbirthday__icontains=keyword) |
                Q(cemail__icontains=keyword) |
                Q(cphone__icontains=keyword) |
                Q(caddr__icontains=keyword))
        resultList = students.objects.filter(query).order_by('cid')
        
        # 測試若無資料時，清空列表
        # resultList = []
    else:
        resultList = students.objects.all().order_by('cid')    
    for student in resultList:
        print(model_to_dict(student))
    #resultList = [] # 測試若無資料時，清空列表
    status = True
    errormessage = ""
    if not resultList:
        errormessage = "查無資料."
        status = False
        data_count = 0
    else:
        data_count = resultList.count() # 計算目前資料筆數

    # 分頁設定，每頁顯示3筆
    from django.core.paginator import Paginator
    paginator = Paginator(resultList, 3) # 每頁顯示3筆
    page_number = request.GET.get('page') # 取得目前頁碼
    page_obj = paginator.get_page(page_number) # 取得目前頁面的資料物件
    
    # 說明:
    # page_obj 是一個包含該頁資料的物件
    # page_obj.number 目前頁碼
    # page_obj.paginator.num_pages 總頁數
    # page_obj.paginator.page_range 所有可用的頁碼（從 1 開始）
    # page_obj.previous_page_number 上一頁的頁碼
    # page_obj.next_page_number 下一頁的頁碼

    # page_obj.has_next 是否有下一頁
    # page_obj.has_previous 是否有上一頁
    # page_obj.object_list 該頁的資料


    # return HttpResponse("This is the index view.")
    return render(request, 'index.html', locals())

from django.shortcuts import redirect
def post(request):
    if request.method == 'POST':
        cname = request.POST.get('cname')
        csex = request.POST.get('csex')
        cbirthday = request.POST.get('cbirthday')
        cemail = request.POST.get('cemail')
        cphone = request.POST.get('cphone')
        caddr = request.POST.get('caddr')
        print(f'cname: {cname}, csex: {csex}, cbirthday: {cbirthday}, cemail: {cemail}, cphone: {cphone}, caddr: {caddr}')
        # # 新增學生資料到資料庫
        add = students(
            cname=cname,
            csex=csex,
            cbirthday=cbirthday,
            cemail=cemail,
            cphone=cphone,
            caddr=caddr
        )
        add.save()
        return redirect('index') # 新增完成後，導向首頁
    else:
        # return HttpResponse("Hello")
        return render(request, 'post.html')

def edit(request, id):
    if request.method == 'POST':
        cname = request.POST.get('cname')
        csex = request.POST.get('csex')
        cbirthday = request.POST.get('cbirthday')
        cemail = request.POST.get('cemail')
        cphone = request.POST.get('cphone')
        caddr = request.POST.get('caddr')
        print(f'id: {id}')
        print(f'cname: {cname}, csex: {csex}, cbirthday: {cbirthday}, cemail: {cemail}, cphone: {cphone}, caddr: {caddr}')
        # 更新指定id的學生資料
        students.objects.filter(cid=id).update(
            cname=cname,
            csex=csex,
            cbirthday=cbirthday,
            cemail=cemail,
            cphone=cphone,
            caddr=caddr
        )
        # return HttpResponse(f"This is a POST request for editing student")
        return redirect('index') # 更新完成後，導向首頁
    else:
        print(f"id: {id}")
        # 取得指定id的學生資料
        obj_data = students.objects.get(cid=id)
        print(model_to_dict(obj_data))
        # return HttpResponse(f"This is the edit view")
        return render(request, 'edit.html', locals())

def delete(request, id):
    if request.method == 'POST':
        print(f"id: {id}")
        students.objects.filter(cid=id).delete() # 刪除指定id的學生資料
        # return HttpResponse(f"This is a POST request for deleting student")
        return redirect('index') # 刪除完成後，導向首頁
    else:
        print(f"id: {id}")
        # 取得指定id的學生資料
        obj_data = students.objects.get(cid=id)
        print(model_to_dict(obj_data))
        # return HttpResponse(f"This is the delete view")
        return render(request, 'delete.html', locals())       

from django.http import JsonResponse
def getAllItems(request):
    resultList = students.objects.all().order_by('cid')   
    # for item in resultList:
    #     print(model_to_dict(item))
    # 目的:將queryset轉換為list，以便JsonResponse可以正確處理
    resultList = list(resultList.values()) # 內的元素從QuerySet物件轉換為字典(dict)
    print(resultList)
    return JsonResponse(resultList, safe=False)
    # safe=True:只允許傳遞dict
    # safe=False:允許傳遞非dict的資料，例如list

def getItem(request, id):
    print(f"id: {id}")
    try:
        obj_data = students.objects.get(cid=id) #取得指定id的學生資料
        resultDict = model_to_dict(obj_data) # 將QuerySet物件轉換為字典(dict)
        return JsonResponse(resultDict, safe=True)
    except:
        return JsonResponse({'error': 'Student not found'}, status=404)
    # return HttpResponse(f"This is the getItem view for id")

from django.views.decorators.csrf import csrf_exempt
# 取消 CSRF 驗證，允許跨站請求
@csrf_exempt
def createItem(request):
    try:
        if request.method == 'GET':
            cname = request.GET['cname']
            csex = request.GET['csex']
            cbirthday = request.GET['cbirthday']
            cemail = request.GET['cemail']
            cphone = request.GET['cphone']
            caddr = request.GET['caddr']
            print("........GET......")
            print(f'cname: {cname}, csex: {csex}, cbirthday: {cbirthday}, cemail: {cemail}, cphone: {cphone}, caddr: {caddr}')
        elif request.method == 'POST':
            cname = request.POST['cname']
            csex = request.POST['csex']
            cbirthday = request.POST['cbirthday']
            cemail = request.POST['cemail']
            cphone = request.POST['cphone']
            caddr = request.POST['caddr']
            print("........POST......")
            print(f'cname: {cname}, csex: {csex}, cbirthday: {cbirthday}, cemail: {cemail}, cphone: {cphone}, caddr: {caddr}')
    except:
        return JsonResponse({'error': 'Invalid request'}, status=400)

    try:
        # orm 建立新的學生資料
        students.objects.create(
            cname=cname,
            csex=csex,
            cbirthday=cbirthday,
            cemail=cemail,
            cphone=cphone,
            caddr=caddr
        )
        return JsonResponse({"message":"Student created successfully"}, safe=True)
    except:
        return JsonResponse({'message': 'Failed to create student'}, status=400)

    # return HttpResponse(f"This is the createItem view")

@csrf_exempt
def updateItem(request, id):
    try:
        obj_data = students.objects.get(cid=id) #取得指定id的學生資料
        if request.method == 'GET':
            cname = request.GET['cname']
            csex = request.GET['csex']
            cbirthday = request.GET['cbirthday']
            cemail = request.GET['cemail']
            cphone = request.GET['cphone']
            caddr = request.GET['caddr']
        elif request.method == 'POST':
            cname = request.POST['cname']
            csex = request.POST['csex']
            cbirthday = request.POST['cbirthday']
            cemail = request.POST['cemail']
            cphone = request.POST['cphone']
            caddr = request.POST['caddr']
        obj_data.cname = cname
        obj_data.csex = csex
        obj_data.cbirthday = cbirthday
        obj_data.cemail = cemail
        obj_data.cphone = cphone
        obj_data.caddr = caddr
        obj_data.save()
        return JsonResponse({"message":"Student updated successfully"}, safe=True)
    except students.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    except:
        return JsonResponse({'message': 'Failed to update student'}, status=400)

@csrf_exempt
def deleteItem(request, id):
    try:
        obj_data = students.objects.get(cid=id) #取得指定id的學生資料
        obj_data.delete()
        return JsonResponse({"message":"Student deleted successfully"}, safe=True)
    except students.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    except:
        return JsonResponse({'message': 'Failed to delete student'}, status=400)