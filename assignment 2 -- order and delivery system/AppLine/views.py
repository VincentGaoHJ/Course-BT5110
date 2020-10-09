from django.shortcuts import render
from .models import Item, Stock, Warehouse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.db.models import F
import itertools
from django.db import IntegrityError


# Auxiliary function
def get_para(request):
    i_name = request.GET.get('i_name', '')
    w_name = request.GET.get('w_name', '')
    i_id_str = request.GET.get('i_id', '')
    w_id_str = request.GET.get('w_id', '')
    qty_str = request.GET.get('qty', '')

    operation_type = request.GET.get('type', '')

    i_id = int(i_id_str) if len(i_id_str) > 0 else i_id_str
    w_id = int(w_id_str) if len(w_id_str) > 0 else w_id_str
    qty = int(qty_str) if len(qty_str) > 0 else qty_str
    return i_id, w_id, qty, operation_type, i_name, w_name


# Main Page
def index(request):
    return render(request, 'AppLine/index.html')


# Display the Inventory
def result(request):
    item_str, item_id, warehouse_str, _, _ = get_para(request)

    results = Stock.objects.filter(
        w__w_name=warehouse_str,
        i__i_name=item_str,
        i__i_id=item_id
    )

    results = [(r.i.i_name, r.i.i_id, r.w.w_name, r.s_qty) for r in results]

    result_dict = {'records': results}
    print(result_dict)
    return render(request, 'AppLine/result.html', result_dict)


# Operation Page
def operation(request):
    i_id, w_id, qty, operation_type, _, _ = get_para(request)

    w_id_obj = Warehouse.objects.get(w_id=w_id)
    i_id_obj = Item.objects.get(i_id=i_id)

    tmp_obj = Stock.objects.filter(
        i=i_id_obj, w=w_id_obj)

    # Check whether there is stock in the database
    try:
        ori_qty = tmp_obj[0].s_qty
    except IndexError as e:
        ori_qty = 0

    item_info = {
        'itemId': i_id,
        'WarehouseId': w_id,
        'item': i_id_obj.i_name,
        'Warehouse': w_id_obj.w_name,
        'qty': 'NA',
    }

    message, sub_message, obj, created = '', '', None, False
    if operation_type == 'order':
        if ori_qty == 0:
            message = 'Insufficient Stock'
            sub_message = 'We are sorry to inform you that there are no product in the selected warehouse, ' \
                          'so we cannot perform order for you, please re-enter transaction information.'
        else:
            try:
                message = 'Your line order or delivery has been accepted'
                sub_message = 'We are glad to inform you that your order has been approved,' \
                              'and we have enough stocks to satisfy your demand.'
                update_qty = ori_qty - qty
                tmp_obj.update(s_qty=update_qty)
                item_info['qty'] = update_qty
            except IntegrityError as e:
                message = 'Insufficient stock'
                sub_message = 'We are sorry to inform you that we don\'t have enough stocks in the ' \
                              'selected warehouse to satisfy your order, please re-enter your transaction information.'

    elif operation_type == 'delivery':
        if ori_qty == 0:
            try:
                message = 'Your line order or delivery has been accepted'
                sub_message = 'We are glad to inform you that your delivery has been approved, ' \
                              'this is a new item for the selected warehouse.'
                Stock.objects.create(i=i_id_obj, w=w_id_obj, s_qty=qty)
                item_info['qty'] = qty
            except Exception as e:
                message = e
        else:
            try:
                message = 'Your line order or delivery has been accepted'
                sub_message = 'We are glad to inform you that your delivery has been approved, ' \
                              'the inventory quantity of this product in this warehouse has increased.'
                update_qty = ori_qty + qty
                tmp_obj.update(s_qty=update_qty)
                item_info['qty'] = update_qty
            except Exception as e:
                message = e

    else:
        raise Exception

    result_dict = {'message': message,
                   'subMessage': sub_message,
                   'itemInfo': item_info}
    return render(request, 'AppLine/info.html', result_dict)


@csrf_exempt
def inventory(request):
    _, _, _, _, i_name, w_name = get_para(request)
    if len(i_name) != 0 and len(w_name) != 0:
        tmp_obj = Stock.objects.filter(w__w_name__icontains=w_name,
                                       i__i_name__icontains=i_name)
    elif len(i_name) != 0:
        tmp_obj = Stock.objects.filter(i__i_name__icontains=i_name)
    elif len(w_name) != 0:
        tmp_obj = Stock.objects.filter(i__i_name__icontains=w_name)
    else:
        tmp_obj = Stock.objects.all()[:20]
    i_name_lst = []
    i_id_lst = []
    w_name_lst = []
    w_id_lst = []
    s_qty_lst = []
    for r in tmp_obj:
        i_name_lst.append(r.i.i_name)
        i_id_lst.append(r.i.i_id)
        w_name_lst.append(r.w.w_name)
        w_id_lst.append(r.w.w_id)
        s_qty_lst.append(r.s_qty)
    result_dict = {
        'i_name': i_name_lst,
        'i_id': i_id_lst,
        'w_name': w_name_lst,
        'w_id': w_id_lst,
        's_qty': s_qty_lst

    }
    return JsonResponse(result_dict)


@csrf_exempt
def new_product(request):
    _, _, _, _, i_name, w_name = get_para(request)

    if len(i_name) == 0 or len(w_name) == 0:
        print("请同时输入仓库信息和产品信息以便缩小查找范围")
        raise Exception

    i_obj_lst = Item.objects.filter(i_name__icontains=i_name)
    w_obj_lst = Warehouse.objects.filter(w_name__icontains=w_name)

    if len(i_obj_lst) == 0 or len(w_obj_lst) == 0:
        print('找不到匹配的仓库或者产品，请重新输入')
        raise Exception
    i_name_lst = []
    i_id_lst = []
    w_name_lst = []
    w_id_lst = []
    for (i_obj, w_obj) in itertools.product(i_obj_lst, w_obj_lst):
        try:
            Stock.objects.get(w=w_obj, i=i_obj)
        except Exception as e:
            i_name_lst.append(i_obj.i_name)
            i_id_lst.append(i_obj.i_id)
            w_name_lst.append(w_obj.w_name)
            w_id_lst.append(w_obj.w_id)

    result_dict = {
        'i_name': i_name_lst,
        'i_id': i_id_lst,
        'w_name': w_name_lst,
        'w_id': w_id_lst}
    return JsonResponse(result_dict)


def transaction(request):
    i_id, w_id, _, _, _, _ = get_para(request)
    result_dict = {
        'item_id': i_id,
        'warehouse_id': w_id
    }
    return render(request, 'AppLine/transaction.html', result_dict)
