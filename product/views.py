from django.shortcuts import render, redirect
from .models import ProductForm,SUPERCATEGORY_CHOICES,Category,Cart,Purchase
from django.http import JsonResponse, HttpResponse,Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from users.models import User
from users.forms import AddressForm
from instamojo_wrapper import Instamojo
from django.conf import settings
from django.urls import reverse
from datetime import datetime



def mainpage(request):
    products = {}
    for category in SUPERCATEGORY_CHOICES:
        all_subcategory = Category.objects.filter(superCategory=category[0])
        for subcategory in all_subcategory:
            products.update({subcategory: ProductForm.objects.filter(category=subcategory).order_by('-uploadedDate')})

    return render(request, 'product/mainpage.html', {'products': products})


# def home(request):
#     return render(request, 'users/home.html', {})



def productpage(request,product_id):
    cart_obj = Cart.objects.filter(user=request.user.id, is_paid__exact='no').first()
    if cart_obj:
        product_obj = ProductForm.objects.filter(id=product_id).first()
        purchase_obj = Purchase.objects.filter(cart=cart_obj, name=product_obj).first()
        if purchase_obj:
            product_exist = 'Yes'
        else:
            product_exist = 'No'
    else:
        product_exist= 'No'
    return render(request, 'product/productpage.html', {'product_detail': ProductForm.objects.filter(id=product_id)[0], 'product_exist': product_exist})   #because filter returns an array


@csrf_exempt
def add_to_cart(request):
    if request.method == 'POST':
        product = request.POST
        product_id = product['product_id']
        product_price = product['product_price']
        user_id = request.user.id
        cart_obj = Cart.objects.filter(user=user_id, is_paid__exact='no').first()


        if cart_obj:
            if cart_obj.transaction_id != '':
                response = settings.INSTAMOJO_API.payment_request_status(cart_obj.transaction_id)
                if response['payment_request']['status'] == 'Completed' and response['payment_request']['payments'][0]['status'] == 'Credit':
                    cart_obj.transaction_id = response['payment_request']['payments'][0]['payment_id']
                    cart_obj.is_paid = 'yes'
                    cart_obj.save()
                else:
                    cart_obj.transaction_id = ''
                    cart_obj.save()
                    purchases = Purchase.objects.filter(cart=cart_obj)

                    for item in purchases:
                        # print("add to cart function")
                        product = ProductForm.objects.filter(id=item.name.id).first()
                        product.stock = product.stock + item.quantity
                        product.save()


        cart_obj = Cart.objects.filter(user=user_id, is_paid__exact='no').first()
        product_obj = ProductForm.objects.filter(id=product_id).first()
        user_obj = User.objects.filter(id=user_id).first()

        if cart_obj:
            product_exist = Purchase.objects.filter(cart=cart_obj,name=product_obj).first()
            if product_exist:
                cart_obj.total_payment = cart_obj.total_payment - (product_exist.quantity)*(product_exist.price_per_item) + (product_exist.quantity+1)*(product_obj.price)
                cart_obj.save()
                product_exist.quantity += 1
                product_exist.price_per_item = product_obj.price
                product_exist.save()
            else:
                new_product = Purchase.objects.create(cart=cart_obj,name=product_obj,quantity=1,price_per_item=product_obj.price)
                cart_obj.total_payment += product_obj.price
                cart_obj.save()
        else:
            cart_obj = Cart.objects.create(user=user_obj,address='',mobno=0,total_payment=product_obj.price,is_paid='no')
            new_product = Purchase.objects.create(cart=cart_obj,name=product_obj,quantity=1,price_per_item=product_obj.price)
        return JsonResponse({'status': 'OK'})
    else:
        raise Http404("Page not found")


@login_required(login_url='mainpage')
def cart(request):
    cart_obj = Cart.objects.filter(user=request.user.id, is_paid__exact='no').first()
    product_prices = []
    total_amount = 0
    ensure_stock = ''
    if not cart_obj:
        purchases = ''
    else:
        if cart_obj.transaction_id != '':
            response = settings.INSTAMOJO_API.payment_request_status(cart_obj.transaction_id)
            if response['payment_request']['status'] == 'Completed' and response['payment_request']['payments'][0]['status'] == 'Credit':
                purchases = ''
                cart_obj.transaction_id = response['payment_request']['payments'][0]['payment_id']
                cart_obj.is_paid = 'yes'
                cart_obj.save()
            else:
                cart_obj.transaction_id = ''
                cart_obj.save()
                purchases = Purchase.objects.filter(cart=cart_obj)

                for item in purchases:
                    # print("cart function")
                    product = ProductForm.objects.filter(id=item.name.id).first()
                    product.stock = product.stock + item.quantity
                    product.save()

                if not purchases:
                    purchases = ''
                else:
                    for product in purchases:
                        if product.quantity > product.name.stock:
                            ensure_stock = ''
                        else:
                            ensure_stock = 'ok'
                        product_prices.append(product.quantity*product.name.price)
                        total_amount += product.quantity*product.name.price
                        product.price_per_item = product.name.price
                        product.save()
                    cart_obj.total_payment = total_amount
                    cart_obj.save()
        else:
            purchases = Purchase.objects.filter(cart=cart_obj)
            if not purchases:
                purchases = ''
            else:
                for product in purchases:
                    if product.quantity > product.name.stock:
                        ensure_stock = ''
                    else:
                        ensure_stock = 'ok'
                    product_prices.append(product.quantity*product.name.price)
                    total_amount += product.quantity*product.name.price
                    product.price_per_item = product.name.price
                    product.save()
                cart_obj.total_payment = total_amount
                cart_obj.save()
    if purchases == '':
        return render(request, 'product/cart.html', {'purchases': zip(purchases,product_prices),'total_payment': total_amount,'is_empty': 'Yes','ensure_stock': ensure_stock})
    else:
        return render(request, 'product/cart.html', {'purchases': zip(purchases,product_prices),'total_payment': total_amount,'is_empty': 'No','ensure_stock': ensure_stock})


@csrf_exempt
@login_required(login_url='mainpage')
def update_cart(request):
    if request.method == 'POST':
        product = request.POST
        product_id = product['product_id']
        new_quantity = product['new_quantity']
        cart_obj = Cart.objects.filter(user=request.user.id, is_paid__exact='no').first()
        product_obj = ProductForm.objects.filter(id=product_id).first()
        purchase_obj = Purchase.objects.filter(cart=cart_obj, name=product_obj).first()
        cart_obj.total_payment = cart_obj.total_payment - (purchase_obj.quantity)*(purchase_obj.price_per_item) + (int(new_quantity))*(product_obj.price)
        cart_obj.save()
        purchase_obj.quantity = new_quantity
        purchase_obj.price_per_item = product_obj.price
        purchase_obj.save()

        return JsonResponse({'status': 'OK'})
    else:
        raise Http404("Page not found")



@csrf_exempt
@login_required(login_url='mainpage')
def delete_item(request):
    if request.method == 'POST':
        product = request.POST
        product_id = product['product_id']

        cart_obj = Cart.objects.filter(user=request.user.id, is_paid__exact='no').first()
        product_obj = ProductForm.objects.filter(id=product_id).first()
        purchase_obj = Purchase.objects.filter(cart=cart_obj, name=product_obj).first()
        cart_obj.total_payment = cart_obj.total_payment - (purchase_obj.quantity)*(purchase_obj.price_per_item)
        cart_obj.save()
        purchase_obj.delete()
        purchases = Purchase.objects.filter(cart=cart_obj)
        if not purchases:
            cart_obj.delete()
        return JsonResponse({'status': 'OK'})
    else:
        raise Http404("Page not found")


@login_required(login_url='mainpage')
def checkout_cart(request):
    if request.method == 'POST':
        form = AddressForm()
        return render(request, 'product/checkout_cart.html', {'address_form': form})
    else:
        raise Http404("Page not found")


@login_required(login_url='mainpage')
def payment(request):
    if request.method == 'POST':
        shipping_details = request.POST
        cart_obj = Cart.objects.filter(user=request.user.id, is_paid__exact='no').first()
        cart_obj.address = shipping_details['address']
        cart_obj.mobno = shipping_details['mobno']
        cart_obj.save()
        purchases = Purchase.objects.filter(cart=cart_obj)
        for item in purchases:
            product = ProductForm.objects.filter(id=item.name.id).first()
            # print(product.stock)
            product.stock = product.stock - item.quantity
            product.save()
            # print(product.stock)
        response = insta(request.user.email,request.user.username,cart_obj.mobno,request.build_absolute_uri(reverse('payment_details')),cart_obj.total_payment)
        # print(response)
        cart_obj.transaction_id = response['payment_request']['id']
        cart_obj.date = datetime.now()
        cart_obj.save()
        return redirect(response['payment_request']['longurl'])
    else:
        raise Http404("Page not found")



def insta(email, name, phone, redirect_url, amount):
    response = settings.INSTAMOJO_API.payment_request_create(
                    amount=str(amount),
                    purpose='ordering_items',
                    buyer_name=name,
                    send_email=True,
                    email=email,
                    send_sms=True,
                    phone=phone,
                    redirect_url=redirect_url,
                    #webhook=webhook, impp - webhook function must be csrf_exempt as instamojo server
                    # sends a post request to our server but without csrf token
            )
    return response


@login_required(login_url='mainpage')
def payment_details(request):
    try:
        payment_status = request.GET['payment_status']
        payment_request_id = request.GET['payment_request_id']
        payment_id = request.GET['payment_id']
    except:
        raise Http404('Page not found')

    if payment_status == 'Credit':
        product_prices = []
        cart_obj = Cart.objects.filter(user=request.user.id,is_paid__exact='no',transaction_id__exact=payment_request_id).first()
        cart_obj.transaction_id = payment_id
        cart_obj.is_paid = 'yes'
        cart_obj.save()
        purchases = Purchase.objects.filter(cart=cart_obj)
        for product in purchases:
            product_prices.append(product.quantity*product.price_per_item)
        return render(request, 'product/payment_details.html', {'cart': cart_obj, 'purchases': zip(purchases,product_prices)})
